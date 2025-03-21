from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTabWidget, QFormLayout, QCheckBox, QGroupBox,
                             QLabel, QSpinBox, QDoubleSpinBox, QComboBox,
                             QMessageBox, QScrollArea, QLineEdit)
from PyQt6.QtCore import Qt
from src.database.database import DatabaseManager
from src.utils.logger import setup_logger
from src.utils.language_manager import LanguageManager
import json
import os

logger = setup_logger(__name__)

class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.language_manager = LanguageManager()
        self.settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'settings.json')
        self.settings = self._load_settings()
        self._init_ui()
        self.language_manager.language_changed.connect(self._on_language_changed)
    
    def _on_language_changed(self, language):
        """Handle language change event by updating all UI elements."""
        logger.info(f"Updating UI for language: {language}")
        
        # Update tab titles
        for i, title in enumerate([
            'settings.project_settings',
            'settings.machine_settings',
            'settings.operator_settings',
            'settings.financial_settings',
            'settings.system_settings'
        ]):
            self.tab_widget.setTabText(i, self.language_manager.translate(title))
        
        # Update save button
        self.save_btn.setText(self.language_manager.translate('settings.save'))
        
        # Update project settings
        self.billing_group.setTitle(self.language_manager.translate('project.billing_type'))
        self.required_group.setTitle(self.language_manager.translate('project.required_fields'))
        self.optional_group.setTitle(self.language_manager.translate('project.optional_fields'))
        
        # Update machine settings
        self.machine_required_group.setTitle(self.language_manager.translate('machine.required_fields'))
        
        # Update operator settings
        self.operator_required_group.setTitle(self.language_manager.translate('operator.required_fields'))
        self.operator_optional_group.setTitle(self.language_manager.translate('operator.optional_fields'))
        
        # Update financial settings
        self.currency_group.setTitle(self.language_manager.translate('financial.currency_settings'))
        self.tax_group.setTitle(self.language_manager.translate('financial.tax_settings'))
        self.invoice_group.setTitle(self.language_manager.translate('financial.invoice_settings'))
        self.payment_group.setTitle(self.language_manager.translate('financial.payment_settings'))
        
        self.currency_label.setText(self.language_manager.translate('financial.currency_name') + ":")
        self.currency_symbol_label.setText(self.language_manager.translate('financial.currency_symbol') + ":")
        self.tax_rate_label.setText(self.language_manager.translate('financial.tax_rate') + ":")
        self.invoice_prefix_label.setText(self.language_manager.translate('financial.invoice_prefix') + ":")
        self.invoice_number_length_label.setText(self.language_manager.translate('financial.invoice_number_length') + ":")
        self.payment_terms_label.setText(self.language_manager.translate('financial.default_payment_terms') + ":")
        
        # Update system settings
        self.appearance_group.setTitle(self.language_manager.translate('system.appearance'))
        self.datetime_group.setTitle(self.language_manager.translate('system.date_time'))
        self.backup_group.setTitle(self.language_manager.translate('system.backup_settings'))
        
        self.theme_label.setText(self.language_manager.translate('system.theme') + ":")
        self.language_label.setText(self.language_manager.translate('system.language') + ":")
        self.date_format_label.setText(self.language_manager.translate('system.date_format') + ":")
        self.time_format_label.setText(self.language_manager.translate('system.time_format') + ":")
        self.auto_backup.setText(self.language_manager.translate('system.enable_auto_backup'))
        self.backup_interval_label.setText(self.language_manager.translate('system.backup_interval') + ":")
        self.max_backup_files_label.setText(self.language_manager.translate('system.max_backup_files') + ":")
        
        # Update checkboxes in project settings
        for field in self.project_required_fields:
            checkbox = self.required_group.findChild(QCheckBox, field)
            if checkbox:
                checkbox.setText(self.language_manager.translate(f'project.{field}'))
        
        for field in self.project_optional_fields:
            checkbox = self.optional_group.findChild(QCheckBox, field)
            if checkbox:
                checkbox.setText(self.language_manager.translate(f'project.{field}'))
        
        # Update checkboxes in machine settings
        for field in self.machine_required_fields:
            checkbox = self.machine_required_group.findChild(QCheckBox, field)
            if checkbox:
                checkbox.setText(self.language_manager.translate(f'machine.{field}'))
        
        # Update checkboxes in operator settings
        for field in self.operator_required_fields:
            checkbox = self.operator_required_group.findChild(QCheckBox, field)
            if checkbox:
                checkbox.setText(self.language_manager.translate(f'operator.{field}'))
        
        for field in self.operator_optional_fields:
            checkbox = self.operator_optional_group.findChild(QCheckBox, field)
            if checkbox:
                checkbox.setText(self.language_manager.translate(f'operator.{field}'))
        
        logger.info("UI update complete")
    
    def _load_settings(self):
        """Load settings from JSON file."""
        default_settings = {
            'project': {
                'billing_type': 'area',  # area or time
                'required_fields': {
                    'name': True,
                    'contract_amount': True,
                    'start_date': True,
                    'end_date': True,
                    'total_length': True,
                    'average_depth': True,
                    'average_width': True,
                    'status': True
                },
                'optional_fields': {
                    'description': True,
                    'client_name': True,
                    'client_contact': True,
                    'location': True,
                    'notes': True
                }
            },
            'machine': {
                'required_fields': {
                    'name': True,
                    'model': True,
                    'purchase_date': True,
                    'purchase_price': True,
                    'fuel_consumption_rate': True,
                    'fuel_cost_per_liter': True,
                    'maintenance_cost_per_hour': True,
                    'trenching_depth': True,
                    'trenching_width': True,
                    'maximum_speed': True,
                    'weight': True,
                    'status': True
                }
            },
            'operator': {
                'required_fields': {
                    'name': True,
                    'hourly_rate': True,
                    'overtime_rate': True,
                    'overtime_threshold': True
                },
                'optional_fields': {
                    'contact': True,
                    'skills': True,
                    'notes': True
                }
            },
            'financial': {
                'currency': 'ریال',
                'currency_symbol': 'ریال ',
                'tax_rate': 9.0,
                'default_payment_terms': 30,
                'invoice_prefix': 'INV-',
                'invoice_number_length': 6
            },
            'system': {
                'theme': 'light',
                'language': 'en',
                'date_format': 'YYYY-MM-DD',
                'time_format': 'HH:mm',
                'auto_backup': True,
                'backup_interval': 7,  # days
                'max_backup_files': 5
            }
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    # Merge saved settings with defaults
                    return self._merge_settings(default_settings, saved_settings)
            return default_settings
        except Exception as e:
            logger.error(f"Failed to load settings: {str(e)}")
            return default_settings
    
    def _merge_settings(self, default, saved):
        """Merge saved settings with defaults, preserving defaults for missing keys."""
        merged = default.copy()
        for key, value in saved.items():
            if key in merged:
                if isinstance(value, dict) and isinstance(merged[key], dict):
                    merged[key] = self._merge_settings(merged[key], value)
                else:
                    merged[key] = value
        return merged
    
    def _save_settings(self):
        """Save settings to JSON file."""
        try:
            # Update settings from UI
            # Project settings
            self.settings['project']['billing_type'] = self.billing_type.currentText()
            for field, checkbox in self.project_required_fields.items():
                self.settings['project']['required_fields'][field] = checkbox.isChecked()
            for field, checkbox in self.project_optional_fields.items():
                self.settings['project']['optional_fields'][field] = checkbox.isChecked()
            
            # Machine settings
            for field, checkbox in self.machine_required_fields.items():
                self.settings['machine']['required_fields'][field] = checkbox.isChecked()
            
            # Operator settings
            for field, checkbox in self.operator_required_fields.items():
                self.settings['operator']['required_fields'][field] = checkbox.isChecked()
            for field, checkbox in self.operator_optional_fields.items():
                self.settings['operator']['optional_fields'][field] = checkbox.isChecked()
            
            # Financial settings
            self.settings['financial']['currency'] = self.currency.text()
            self.settings['financial']['currency_symbol'] = self.currency_symbol.text()
            self.settings['financial']['tax_rate'] = self.tax_rate.value()
            self.settings['financial']['default_payment_terms'] = self.payment_terms.value()
            self.settings['financial']['invoice_prefix'] = self.invoice_prefix.text()
            self.settings['financial']['invoice_number_length'] = self.invoice_number_length.value()
            
            # System settings
            self.settings['system']['theme'] = self.theme.currentText()
            new_language = self.language.currentText()
            old_language = self.settings['system']['language']
            self.settings['system']['language'] = new_language
            self.settings['system']['date_format'] = self.date_format.text()
            self.settings['system']['time_format'] = self.time_format.text()
            self.settings['system']['auto_backup'] = self.auto_backup.isChecked()
            self.settings['system']['backup_interval'] = self.backup_interval.value()
            self.settings['system']['max_backup_files'] = self.max_backup_files.value()
            
            # Save to file
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            
            # Update language if changed
            if new_language != old_language:
                logger.info(f"Language changed from {old_language} to {new_language}")
                self.language_manager.set_language(new_language)
                # Force UI update
                self._on_language_changed(new_language)
            
            logger.info("Settings saved successfully")
            QMessageBox.information(self, 
                                  self.language_manager.translate('settings.success'),
                                  self.language_manager.translate('settings.settings_saved'))
        except Exception as e:
            logger.error(f"Failed to save settings: {str(e)}")
            QMessageBox.critical(self,
                               self.language_manager.translate('settings.error'),
                               self.language_manager.translate('settings.save_failed').format(str(e)))
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs
        self.tab_widget.addTab(self._create_project_settings(), self.language_manager.translate('settings.project_settings'))
        self.tab_widget.addTab(self._create_machine_settings(), self.language_manager.translate('settings.machine_settings'))
        self.tab_widget.addTab(self._create_operator_settings(), self.language_manager.translate('settings.operator_settings'))
        self.tab_widget.addTab(self._create_financial_settings(), self.language_manager.translate('settings.financial_settings'))
        self.tab_widget.addTab(self._create_system_settings(), self.language_manager.translate('settings.system_settings'))
        
        layout.addWidget(self.tab_widget)
        
        # Save button
        self.save_btn = QPushButton(self.language_manager.translate('settings.save'))
        self.save_btn.clicked.connect(self._save_settings)
        layout.addWidget(self.save_btn)
    
    def _create_project_settings(self):
        """Create project settings tab."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Billing type
        self.billing_group = QGroupBox(self.language_manager.translate('project.billing_type'))
        billing_layout = QFormLayout()
        self.billing_type = QComboBox()
        self.billing_type.addItems(['area', 'time'])
        self.billing_type.setCurrentText(self.settings['project']['billing_type'])
        billing_layout.addRow(self.language_manager.translate('project.billing_type') + ":", self.billing_type)
        self.billing_group.setLayout(billing_layout)
        layout.addWidget(self.billing_group)
        
        # Required fields
        self.required_group = QGroupBox(self.language_manager.translate('project.required_fields'))
        required_layout = QVBoxLayout()
        self.project_required_fields = {}
        for field, required in self.settings['project']['required_fields'].items():
            checkbox = QCheckBox(self.language_manager.translate(f'project.{field}'))
            checkbox.setChecked(required)
            self.project_required_fields[field] = checkbox
            required_layout.addWidget(checkbox)
        self.required_group.setLayout(required_layout)
        layout.addWidget(self.required_group)
        
        # Optional fields
        self.optional_group = QGroupBox(self.language_manager.translate('project.optional_fields'))
        optional_layout = QVBoxLayout()
        self.project_optional_fields = {}
        for field, enabled in self.settings['project']['optional_fields'].items():
            checkbox = QCheckBox(self.language_manager.translate(f'project.{field}'))
            checkbox.setChecked(enabled)
            self.project_optional_fields[field] = checkbox
            optional_layout.addWidget(checkbox)
        self.optional_group.setLayout(optional_layout)
        layout.addWidget(self.optional_group)
        
        layout.addStretch()
        scroll.setWidget(content)
        return scroll
    
    def _create_machine_settings(self):
        """Create machine settings tab."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Required fields
        self.machine_required_group = QGroupBox(self.language_manager.translate('machine.required_fields'))
        required_layout = QVBoxLayout()
        self.machine_required_fields = {}
        for field, required in self.settings['machine']['required_fields'].items():
            checkbox = QCheckBox(self.language_manager.translate(f'machine.{field}'))
            checkbox.setChecked(required)
            self.machine_required_fields[field] = checkbox
            required_layout.addWidget(checkbox)
        self.machine_required_group.setLayout(required_layout)
        layout.addWidget(self.machine_required_group)
        
        layout.addStretch()
        scroll.setWidget(content)
        return scroll
    
    def _create_operator_settings(self):
        """Create operator settings tab."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Required fields
        self.operator_required_group = QGroupBox(self.language_manager.translate('operator.required_fields'))
        required_layout = QVBoxLayout()
        self.operator_required_fields = {}
        for field, required in self.settings['operator']['required_fields'].items():
            checkbox = QCheckBox(self.language_manager.translate(f'operator.{field}'))
            checkbox.setChecked(required)
            self.operator_required_fields[field] = checkbox
            required_layout.addWidget(checkbox)
        self.operator_required_group.setLayout(required_layout)
        layout.addWidget(self.operator_required_group)
        
        # Optional fields
        self.operator_optional_group = QGroupBox(self.language_manager.translate('operator.optional_fields'))
        optional_layout = QVBoxLayout()
        self.operator_optional_fields = {}
        for field, enabled in self.settings['operator']['optional_fields'].items():
            checkbox = QCheckBox(self.language_manager.translate(f'operator.{field}'))
            checkbox.setChecked(enabled)
            self.operator_optional_fields[field] = checkbox
            optional_layout.addWidget(checkbox)
        self.operator_optional_group.setLayout(optional_layout)
        layout.addWidget(self.operator_optional_group)
        
        layout.addStretch()
        scroll.setWidget(content)
        return scroll
    
    def _create_financial_settings(self):
        """Create financial settings tab."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Currency settings
        self.currency_group = QGroupBox(self.language_manager.translate('financial.currency_settings'))
        currency_layout = QFormLayout()
        self.currency = QLineEdit(self.settings['financial']['currency'])
        self.currency_symbol = QLineEdit(self.settings['financial']['currency_symbol'])
        self.currency_label = QLabel(self.language_manager.translate('financial.currency_name') + ":")
        self.currency_symbol_label = QLabel(self.language_manager.translate('financial.currency_symbol') + ":")
        currency_layout.addRow(self.currency_label, self.currency)
        currency_layout.addRow(self.currency_symbol_label, self.currency_symbol)
        self.currency_group.setLayout(currency_layout)
        layout.addWidget(self.currency_group)
        
        # Tax settings
        self.tax_group = QGroupBox(self.language_manager.translate('financial.tax_settings'))
        tax_layout = QFormLayout()
        self.tax_rate = QDoubleSpinBox()
        self.tax_rate.setRange(0, 100)
        self.tax_rate.setValue(self.settings['financial']['tax_rate'])
        self.tax_rate.setSuffix("%")
        self.tax_rate_label = QLabel(self.language_manager.translate('financial.tax_rate') + ":")
        tax_layout.addRow(self.tax_rate_label, self.tax_rate)
        self.tax_group.setLayout(tax_layout)
        layout.addWidget(self.tax_group)
        
        # Invoice settings
        self.invoice_group = QGroupBox(self.language_manager.translate('financial.invoice_settings'))
        invoice_layout = QFormLayout()
        self.invoice_prefix = QLineEdit(self.settings['financial']['invoice_prefix'])
        self.invoice_number_length = QSpinBox()
        self.invoice_number_length.setRange(4, 10)
        self.invoice_number_length.setValue(self.settings['financial']['invoice_number_length'])
        self.invoice_prefix_label = QLabel(self.language_manager.translate('financial.invoice_prefix') + ":")
        self.invoice_number_length_label = QLabel(self.language_manager.translate('financial.invoice_number_length') + ":")
        invoice_layout.addRow(self.invoice_prefix_label, self.invoice_prefix)
        invoice_layout.addRow(self.invoice_number_length_label, self.invoice_number_length)
        self.invoice_group.setLayout(invoice_layout)
        layout.addWidget(self.invoice_group)
        
        # Payment settings
        self.payment_group = QGroupBox(self.language_manager.translate('financial.payment_settings'))
        payment_layout = QFormLayout()
        self.payment_terms = QSpinBox()
        self.payment_terms.setRange(0, 365)
        self.payment_terms.setValue(self.settings['financial']['default_payment_terms'])
        self.payment_terms.setSuffix(" days")
        self.payment_terms_label = QLabel(self.language_manager.translate('financial.default_payment_terms') + ":")
        payment_layout.addRow(self.payment_terms_label, self.payment_terms)
        self.payment_group.setLayout(payment_layout)
        layout.addWidget(self.payment_group)
        
        layout.addStretch()
        scroll.setWidget(content)
        return scroll
    
    def _create_system_settings(self):
        """Create system settings tab."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Appearance settings
        self.appearance_group = QGroupBox(self.language_manager.translate('system.appearance'))
        appearance_layout = QFormLayout()
        self.theme = QComboBox()
        self.theme.addItems(['light', 'dark'])
        self.theme.setCurrentText(self.settings['system']['theme'])
        self.language = QComboBox()
        self.language.addItems(['en', 'fa'])
        self.language.setCurrentText(self.settings['system']['language'])
        self.theme_label = QLabel(self.language_manager.translate('system.theme') + ":")
        self.language_label = QLabel(self.language_manager.translate('system.language') + ":")
        appearance_layout.addRow(self.theme_label, self.theme)
        appearance_layout.addRow(self.language_label, self.language)
        self.appearance_group.setLayout(appearance_layout)
        layout.addWidget(self.appearance_group)
        
        # Date and time settings
        self.datetime_group = QGroupBox(self.language_manager.translate('system.date_time'))
        datetime_layout = QFormLayout()
        self.date_format = QLineEdit(self.settings['system']['date_format'])
        self.time_format = QLineEdit(self.settings['system']['time_format'])
        self.date_format_label = QLabel(self.language_manager.translate('system.date_format') + ":")
        self.time_format_label = QLabel(self.language_manager.translate('system.time_format') + ":")
        datetime_layout.addRow(self.date_format_label, self.date_format)
        datetime_layout.addRow(self.time_format_label, self.time_format)
        self.datetime_group.setLayout(datetime_layout)
        layout.addWidget(self.datetime_group)
        
        # Backup settings
        self.backup_group = QGroupBox(self.language_manager.translate('system.backup_settings'))
        backup_layout = QFormLayout()
        self.auto_backup = QCheckBox(self.language_manager.translate('system.enable_auto_backup'))
        self.auto_backup.setChecked(self.settings['system']['auto_backup'])
        self.backup_interval = QSpinBox()
        self.backup_interval.setRange(1, 30)
        self.backup_interval.setValue(self.settings['system']['backup_interval'])
        self.backup_interval.setSuffix(" days")
        self.max_backup_files = QSpinBox()
        self.max_backup_files.setRange(1, 20)
        self.max_backup_files.setValue(self.settings['system']['max_backup_files'])
        self.backup_interval_label = QLabel(self.language_manager.translate('system.backup_interval') + ":")
        self.max_backup_files_label = QLabel(self.language_manager.translate('system.max_backup_files') + ":")
        backup_layout.addRow(self.auto_backup)
        backup_layout.addRow(self.backup_interval_label, self.backup_interval)
        backup_layout.addRow(self.max_backup_files_label, self.max_backup_files)
        self.backup_group.setLayout(backup_layout)
        layout.addWidget(self.backup_group)
        
        layout.addStretch()
        scroll.setWidget(content)
        return scroll 