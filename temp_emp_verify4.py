from core.application import GovSyncApplication
from widgets.employee_records_panel import EmployeeDetailsDialog
from PySide6.QtWidgets import QApplication, QDialog
import time

app = QApplication.instance() or QApplication([])
application = GovSyncApplication()
window = application.create_main_window()
window.show()
app.processEvents()
nav = window.navigation_controller
nav.on_authenticated('user', 'admin')
app.processEvents()
time.sleep(1.0)
sidebar = window.sidebar_column.list_widget
sidebar.setCurrentRow(2)
app.processEvents()
time.sleep(1.5)
panel = window.workspace_stack.widget(2)
print('connected count', panel.table.receivers(panel.table.cellDoubleClicked))

def patched_on_double(row, col):
    print('panel._on_cell_double_clicked invoked', row, col)
    employee = panel.table.get_current_employee(row)
    print('employee', employee)
    panel._show_details(employee)

panel._on_cell_double_clicked = patched_on_double
panel.table.cellDoubleClicked.emit(0, 0)
app.processEvents()
time.sleep(1.0)
dialogs = [w for w in app.topLevelWidgets() if isinstance(w, QDialog) and w.isVisible()]
print('dialogs', [(type(d).__name__, d.objectName(), d.windowTitle()) for d in dialogs])
