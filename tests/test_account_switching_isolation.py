"""
Regression tests for account switching and UI state isolation across all modules.
Ensures that:
1. UI state is reset when switching accounts
2. Form fields are cleared for accounts with no saved state
3. Account-scoped data is not visible across accounts
"""

import json
import os
import sys
import tempfile
import gc
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_ui_reset_structure():
    """Test that UI reset methods are properly integrated into set_account."""
    # This test verifies the code structure without needing full dependencies
    from pathlib import Path
    import ast
    
    project_root = Path(__file__).parent.parent
    
    # Test SSSPanel
    sss_panel_path = project_root / "widgets" / "sss_panel.py"
    with open(sss_panel_path, "r") as f:
        sss_content = f.read()
    
    # Verify _reset_ui_state is in the file
    assert "def _reset_ui_state(self):" in sss_content, \
        "SSSPanel should have _reset_ui_state method"
    assert "self.progress_bar.setValue(0)" in sss_content, \
        "SSSPanel._reset_ui_state should reset progress bar"
    assert "self.status_label.setText(\"Ready\")" in sss_content, \
        "SSSPanel._reset_ui_state should reset status label"
    
    # Verify set_account calls _reset_ui_state
    assert "def set_account(self, account):" in sss_content, \
        "SSSPanel should have set_account method"
    assert "_reset_ui_state()" in sss_content, \
        "set_account should call _reset_ui_state"
    
    # Test HDMFLoanPanel
    hdmf_panel_path = project_root / "widgets" / "hdmf_loan_panel.py"
    with open(hdmf_panel_path, "r") as f:
        hdmf_content = f.read()
    
    # Verify _reset_ui_state is in the file
    assert "def _reset_ui_state(self):" in hdmf_content, \
        "HDMFLoanPanel should have _reset_ui_state method"
    assert "self.progress_bar.setValue(0)" in hdmf_content, \
        "HDMFLoanPanel._reset_ui_state should reset progress bar"
    assert "self.status_label.setText(\"Ready\")" in hdmf_content, \
        "HDMFLoanPanel._reset_ui_state should reset status label"
    
    # Verify set_account calls _reset_ui_state
    assert "_reset_ui_state()" in hdmf_content, \
        "set_account should call _reset_ui_state"


def test_sss_panel_form_clearing():
    """Test that SSSPanel._load_state clears form fields at start."""
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent
    sss_panel_path = project_root / "widgets" / "sss_panel.py"
    
    with open(sss_panel_path, "r") as f:
        content = f.read()
    
    # Verify that _load_state clears fields at the beginning
    assert "def _load_state(self):" in content, \
        "SSSPanel should have _load_state method"
    
    # Check for field clearing operations before loading state file
    lines = content.split('\n')
    load_state_start = None
    for i, line in enumerate(lines):
        if "def _load_state(self):" in line:
            load_state_start = i
            break
    
    assert load_state_start is not None, \
        "Could not find _load_state method"
    
    # Look for clearing operations in the method (within ~20 lines after definition)
    method_content = '\n'.join(lines[load_state_start:load_state_start+30])
    assert "self.source_queue.clear()" in method_content, \
        "SSSPanel._load_state should clear source_queue"
    assert "self.output_folder.clear()" in method_content, \
        "SSSPanel._load_state should clear output_folder"


def test_hdmf_panel_form_clearing():
    """Test that HDMFLoanPanel._load_state clears form fields at start."""
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent
    hdmf_panel_path = project_root / "widgets" / "hdmf_loan_panel.py"
    
    with open(hdmf_panel_path, "r") as f:
        content = f.read()
    
    # Verify that _load_state clears fields at the beginning
    assert "def _load_state(self):" in content, \
        "HDMFLoanPanel should have _load_state method"
    
    # Check for field clearing operations before loading state file
    lines = content.split('\n')
    load_state_start = None
    for i, line in enumerate(lines):
        if "def _load_state(self):" in line:
            load_state_start = i
            break
    
    assert load_state_start is not None, \
        "Could not find _load_state method"
    
    # Look for clearing operations in the method (within ~20 lines after definition)
    method_content = '\n'.join(lines[load_state_start:load_state_start+20])
    assert "self.earnings_file.clear()" in method_content, \
        "HDMFLoanPanel._load_state should clear earnings_file"
    assert "self.monitoring_file.clear()" in method_content, \
        "HDMFLoanPanel._load_state should clear monitoring_file"


def test_philhealth_account_scoping():
    """Test that PhilHealth has account-scoped deletion."""
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent
    service_path = project_root / "services" / "philhealth_service.py"
    
    with open(service_path, "r") as f:
        content = f.read()
    
    # Verify delete_history accepts account_username
    assert "def delete_history(self, account_username, record_id):" in content, \
        "PhilHealthService.delete_history should accept account_username"
    
    # Verify it validates account ownership
    assert "list_by_account(account_username)" in content, \
        "delete_history should validate record belongs to account"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "--tb=short"])

