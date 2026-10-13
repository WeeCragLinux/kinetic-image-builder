from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QRadioButton,
    QVBoxLayout,
    QWizard,
    QWizardPage,
)

from . import project

BASE_DESCRIPTIONS = {
    "ghcr.io/theblack-don/kineticos:default": "AMD and Intel GPUs",
    "ghcr.io/theblack-don/kineticos:nvidia": (
        "NVIDIA GPUs based on Turing or newer: GTX 16 series, and RTX 20, 30, 40 and 50 series"
    ),
    "ghcr.io/theblack-don/kineticos:nvidia-legacy": "NVIDIA GPUs older than the 10 series",
}


def app_label(app: project.App) -> str:
    if app.section == "flatpaks":
        return f"{app.name}  (Flatpak, installed per user)"
    if app.section == "local_rpms":
        return f"{app.name}  (local RPM)"
    if app.name in project.RPMFUSION_APPS:
        return f"{app.name}  (needs RPM Fusion)"
    return app.name


class Page(QWizardPage):
    def __init__(self, wizard: Wizard):
        super().__init__(wizard)
        self.wz = wizard

    def nextId(self) -> int:
        flow = self.wz.flow()
        if self not in flow:
            return self.wz.page_ids[self.wz.review_page]
        index = flow.index(self)
        if index + 1 < len(flow):
            return self.wz.page_ids[flow[index + 1]]
        return -1


class BasePage(Page):
    def __init__(self, wizard: Wizard):
        super().__init__(wizard)
        self.setTitle("Base image")
        self.setSubTitle("Choose the Kineticos image that matches your GPU.")
        layout = QVBoxLayout(self)
        for ref, description in BASE_DESCRIPTIONS.items():
            radio = QRadioButton(ref)
            radio.toggled.connect(lambda checked, r=ref: self.pick(r, checked))
            note = QLabel(description)
            note.setWordWrap(True)
            note.setContentsMargins(24, 0, 0, 10)
            layout.addWidget(radio)
            layout.addWidget(note)
        layout.addStretch()

    def pick(self, ref: str, checked: bool) -> None:
        if checked:
            self.wz.state.base_image = ref
            self.completeChanged.emit()

    def isComplete(self) -> bool:
        return self.wz.state.base_image is not None


class ModulePage(Page):
    def __init__(self, wizard: Wizard, module: project.Module):
        super().__init__(wizard)
        self.module = module
        self.setTitle(module.name)
        self.setSubTitle(module.description)
        layout = QVBoxLayout(self)
        chosen = wizard.state.apps.get(module.name, set())
        self.boxes: list[tuple[project.App, QCheckBox]] = []
        for app in module.apps:
            box = QCheckBox(app_label(app))
            box.setChecked(app.name in chosen)
            box.toggled.connect(self.sync)
            layout.addWidget(box)
            self.boxes.append((app, box))
        layout.addStretch()
        self.sync()

    def sync(self, *_) -> None:
        selected = {app.name for app, box in self.boxes if box.isChecked()}
        if selected:
            self.wz.state.apps[self.module.name] = selected
        else:
            self.wz.state.apps.pop(self.module.name, None)


class OptionalPage(Page):
    def __init__(self, wizard: Wizard):
        super().__init__(wizard)
        self.setTitle("Optional modules")
        self.setSubTitle("These modules are on by default, and none of your selected apps need them.")
        layout = QVBoxLayout(self)
        self.rpm_box = QCheckBox("Disable RPM Fusion (free and nonfree repos)")
        self.terra_box = QCheckBox("Disable Terra (repos only)")
        self.rpm_box.toggled.connect(lambda c: setattr(self.wz.state, "disable_rpmfusion", c))
        self.terra_box.toggled.connect(lambda c: setattr(self.wz.state, "disable_terra", c))
        layout.addWidget(self.rpm_box)
        layout.addWidget(self.terra_box)
        layout.addStretch()

    def initializePage(self) -> None:
        asked = project.questions(self.wz.state)
        self.rpm_box.setVisible("rpmfusion" in asked)
        self.rpm_box.setChecked(self.wz.state.disable_rpmfusion)
        self.terra_box.setVisible("terra" in asked)
        self.terra_box.setChecked(self.wz.state.disable_terra)


class ReviewPage(Page):
    def __init__(self, wizard: Wizard):
        super().__init__(wizard)
        self.setTitle("Review")
        self.setSubTitle("These changes are written to profile.yaml and modules/*.yaml, then dcli-bootc gen runs.")
        layout = QVBoxLayout(self)
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)

    def initializePage(self) -> None:
        self.text.setPlainText(summary(self.wz))


def summary(wizard: Wizard) -> str:
    state = wizard.state
    lines = [f"Base image: {state.base_image}", ""]
    for name, on in project.resolve(wizard.profile, state):
        if not on:
            lines.append(f"off   {name}")
            continue
        apps = sorted(state.apps.get(name, ()))
        lines.append(f"on    {name}: {', '.join(apps) if apps else 'default'}")
    return "\n".join(lines)


class Wizard(QWizard):
    def __init__(self, root: Path):
        super().__init__()
        self.root = root
        self.profile = project.Profile(root)
        self.modules = project.load_modules(root)
        self.add_new_modules()
        self.state = project.Selection()
        self.page_ids: dict[QWizardPage, int] = {}

        self.setWindowTitle("kineticos-plus configurator")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setButtonText(QWizard.WizardButton.FinishButton, "Write changes")
        self.resize(760, 600)

        self.base_page = BasePage(self)
        self.add_page(self.base_page)

        self.module_pages: list[ModulePage] = []
        for name, _ in self.profile.entries:
            module = self.modules.get(name)
            if name == "base" or module is None or not module.apps:
                continue
            page = ModulePage(self, module)
            self.add_page(page)
            self.module_pages.append(page)

        self.optional_page = OptionalPage(self)
        self.add_page(self.optional_page)
        self.review_page = ReviewPage(self)
        self.add_page(self.review_page)

    def add_new_modules(self) -> None:
        known = {name for name, _ in self.profile.entries}
        new_modules = sorted(set(self.modules) - known - {"base"})
        if not new_modules:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("New modules found")
        dialog.setMinimumWidth(380)
        layout = QVBoxLayout(dialog)
        message = QLabel(
            "Select the modules to add to profile.yaml. App modules will remain "
            "disabled unless you select apps from them in the wizard."
        )
        message.setWordWrap(True)
        layout.addWidget(message)

        module_list = QListWidget(dialog)
        for name in new_modules:
            item = QListWidgetItem(name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setToolTip(self.modules[name].description)
            module_list.addItem(item)
        layout.addWidget(module_list)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=dialog,
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Add selected")
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        selected = [
            module_list.item(index).text()
            for index in range(module_list.count())
            if module_list.item(index).checkState() == Qt.CheckState.Checked
        ]
        self.profile.entries.extend((name, False) for name in selected)

    def add_page(self, page: QWizardPage) -> None:
        page_id = len(self.page_ids)
        self.page_ids[page] = page_id
        self.setPage(page_id, page)

    def flow(self) -> list[QWizardPage]:
        pages: list[QWizardPage] = [self.base_page, *self.module_pages]
        if project.questions(self.state):
            pages.append(self.optional_page)
        pages.append(self.review_page)
        return pages

    def accept(self) -> None:
        try:
            project.apply(self.root, self.state, self.modules, self.profile)
        except OSError as error:
            QMessageBox.critical(self, "Could not write files", str(error))
            return
        ok, output = project.generate(self.root)
        if not ok:
            QMessageBox.warning(
                self,
                "Files written, but dcli-bootc gen failed",
                output or "dcli-bootc gen failed.",
            )
            return
        QMessageBox.information(
            self,
            "Done",
            "Files written and dcli-bootc gen completed.\n\nNext step: dcli-bootc build",
        )
        super().accept()


def main(root: Path) -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("kineticos-plus configurator")
    if not (root / "profile.yaml").is_file():
        QMessageBox.critical(None, "kineticos-plus configurator", f"No profile.yaml in {root}")
        return 1
    wizard = Wizard(root)
    wizard.show()
    return app.exec()
