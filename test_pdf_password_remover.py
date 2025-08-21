"""
Test suite for PDF Password Remover application.
Run with: python -m pytest test_pdf_password_remover.py -v
"""

import unittest
import tempfile
import os
import sys
import shutil
from unittest.mock import patch, MagicMock, mock_open
from io import StringIO

# Add the current directory to Python path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the modules to test
from remove_pdf_password import (
    setup_logging, validate_pdf_file, create_backup, remove_password, 
    add_password, _convert_permissions_to_flag, process_batch
)

class TestPDFPasswordRemover(unittest.TestCase):
    """Test cases for the PDF password remover CLI functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_pdf = os.path.join(self.test_dir, "test.pdf")
        self.output_pdf = os.path.join(self.test_dir, "output.pdf")
        
        # Create a fake PDF file for testing
        with open(self.test_pdf, 'wb') as f:
            f.write(b'%PDF-1.4\nFake PDF content for testing')
            
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def test_setup_logging(self):
        """Test logging setup."""
        with patch('logging.basicConfig') as mock_config:
            setup_logging(verbose=False)
            mock_config.assert_called_once()
            
            # Test verbose mode
            setup_logging(verbose=True)
            self.assertEqual(mock_config.call_count, 2)
            
    def test_validate_pdf_file_success(self):
        """Test successful PDF file validation."""
        try:
            validate_pdf_file(self.test_pdf)
        except Exception:
            self.fail("validate_pdf_file raised exception for valid PDF")
            
    def test_validate_pdf_file_not_found(self):
        """Test validation with non-existent file."""
        with self.assertRaises(FileNotFoundError):
            validate_pdf_file("nonexistent.pdf")
            
    def test_validate_pdf_file_not_pdf(self):
        """Test validation with non-PDF file."""
        txt_file = os.path.join(self.test_dir, "test.txt")
        with open(txt_file, 'w') as f:
            f.write("Not a PDF")
            
        with self.assertRaises(ValueError):
            validate_pdf_file(txt_file)
            
    def test_validate_pdf_file_invalid_header(self):
        """Test validation with file that doesn't have PDF header."""
        fake_pdf = os.path.join(self.test_dir, "fake.pdf")
        with open(fake_pdf, 'wb') as f:
            f.write(b'Not a PDF header')
            
        with self.assertRaises(ValueError):
            validate_pdf_file(fake_pdf)
            
    def test_create_backup(self):
        """Test backup file creation."""
        backup_path = create_backup(self.test_pdf)
        
        # Check that backup file exists
        self.assertTrue(os.path.exists(backup_path))
        
        # Check that backup has correct content
        with open(backup_path, 'rb') as f:
            backup_content = f.read()
        with open(self.test_pdf, 'rb') as f:
            original_content = f.read()
            
        self.assertEqual(backup_content, original_content)
        
        # Check that backup filename contains "backup"
        self.assertIn("backup", os.path.basename(backup_path))
        
    def test_create_backup_custom_directory(self):
        """Test backup creation in custom directory."""
        backup_dir = os.path.join(self.test_dir, "backups")
        os.makedirs(backup_dir)
        
        backup_path = create_backup(self.test_pdf, backup_dir)
        
        # Check that backup is in the correct directory
        self.assertEqual(os.path.dirname(backup_path), backup_dir)
        self.assertTrue(os.path.exists(backup_path))
        
    @patch('remove_pdf_password.PdfReader')
    def test_remove_password_not_encrypted(self, mock_reader_class):
        """Test handling of non-encrypted PDF."""
        # Mock PdfReader to simulate non-encrypted PDF
        mock_reader = MagicMock()
        mock_reader.is_encrypted = False
        mock_reader.pages = []
        mock_reader_class.return_value = mock_reader
        
        with patch('builtins.open', mock_open()):
            result = remove_password(self.test_pdf, self.output_pdf, "password", False, True)
            
        self.assertTrue(result)
        
    @patch('remove_pdf_password.PdfReader')
    def test_remove_password_wrong_password(self, mock_reader_class):
        """Test handling of wrong password."""
        # Mock PdfReader to simulate encrypted PDF with wrong password
        mock_reader = MagicMock()
        mock_reader.is_encrypted = True
        mock_reader.decrypt.return_value = False
        mock_reader_class.return_value = mock_reader
        
        result = remove_password(self.test_pdf, self.output_pdf, "wrong_password", False, True)
        
        self.assertFalse(result)
        
    @patch('remove_pdf_password.PdfReader')
    @patch('remove_pdf_password.PdfWriter')
    def test_remove_password_success(self, mock_writer_class, mock_reader_class):
        """Test successful password removal."""
        # Mock PdfReader
        mock_reader = MagicMock()
        mock_reader.is_encrypted = True
        mock_reader.decrypt.return_value = True
        mock_reader.pages = [MagicMock(), MagicMock()]  # Two pages
        mock_reader_class.return_value = mock_reader
        
        # Mock PdfWriter
        mock_writer = MagicMock()
        mock_writer_class.return_value = mock_writer
        
        with patch('builtins.open', mock_open()):
            result = remove_password(self.test_pdf, self.output_pdf, "correct_password", False, True)
            
        self.assertTrue(result)
        
        # Verify that pages were added to writer
        self.assertEqual(mock_writer.add_page.call_count, 2)
        
        # Verify that writer.write was called
        mock_writer.write.assert_called_once()
        
    def test_convert_permissions_to_flag(self):
        """Test permissions flag conversion."""
        # Test all permissions enabled
        permissions = {'print': True, 'modify': True, 'copy': True, 'annotate': True}
        flag = _convert_permissions_to_flag(permissions)
        self.assertEqual(flag, 4 + 8 + 16 + 32)  # 60
        
        # Test no permissions
        permissions = {'print': False, 'modify': False, 'copy': False, 'annotate': False}
        flag = _convert_permissions_to_flag(permissions)
        self.assertEqual(flag, 0)
        
        # Test partial permissions
        permissions = {'print': True, 'copy': True}
        flag = _convert_permissions_to_flag(permissions)
        self.assertEqual(flag, 4 + 16)  # 20

    def test_process_batch_empty_list(self):
        """Test batch processing with empty file list."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            process_batch([], "password")
            output = mock_stdout.getvalue()
            
        self.assertIn("Successful: 0", output)
        self.assertIn("Failed: 0", output)
        
    @patch('remove_pdf_password.remove_password')
    def test_process_batch_mixed_results(self, mock_remove_password):
        """Test batch processing with mixed success/failure."""
        # Mock remove_password to return True for first file, False for second
        mock_remove_password.side_effect = [True, False]
        
        files = ["file1.pdf", "file2.pdf"]
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            process_batch(files, "password")
            output = mock_stdout.getvalue()
            
        self.assertIn("Successful: 1", output)
        self.assertIn("Failed: 1", output)
        self.assertIn("file2.pdf", output)  # Failed file should be listed

class TestPasswordAddition(unittest.TestCase):
    """Test cases for password addition functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_pdf = os.path.join(self.test_dir, "test.pdf")
        self.output_pdf = os.path.join(self.test_dir, "output.pdf")
        
        # Create a fake PDF file for testing
        with open(self.test_pdf, 'wb') as f:
            f.write(b'%PDF-1.4\nFake PDF content for testing')
            
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    @patch('remove_pdf_password.PdfReader')
    @patch('remove_pdf_password.PdfWriter')
    def test_add_password_success(self, mock_writer_class, mock_reader_class):
        """Test successful password addition."""
        # Mock PdfReader
        mock_reader = MagicMock()
        mock_reader.is_encrypted = False
        mock_reader.pages = [MagicMock(), MagicMock()]  # Two pages
        mock_reader_class.return_value = mock_reader
        
        # Mock PdfWriter
        mock_writer = MagicMock()
        mock_writer_class.return_value = mock_writer
        
        with patch('builtins.open', mock_open()):
            result = add_password(self.test_pdf, self.output_pdf, "password123", None, False, True)
            
        self.assertTrue(result)
        
        # Verify that pages were added to writer
        self.assertEqual(mock_writer.add_page.call_count, 2)
        
        # Verify that encryption was applied
        mock_writer.encrypt.assert_called_once()
        
        # Verify that writer.write was called
        mock_writer.write.assert_called_once()
        
    @patch('remove_pdf_password.PdfReader')
    @patch('remove_pdf_password.PdfWriter')
    def test_add_password_with_permissions(self, mock_writer_class, mock_reader_class):
        """Test password addition with custom permissions."""
        mock_reader = MagicMock()
        mock_reader.is_encrypted = False
        mock_reader.pages = [MagicMock()]
        mock_reader_class.return_value = mock_reader
        
        mock_writer = MagicMock()
        mock_writer_class.return_value = mock_writer
        
        permissions = {'print': True, 'modify': False, 'copy': True, 'annotate': False}
        
        with patch('builtins.open', mock_open()):
            result = add_password(self.test_pdf, self.output_pdf, "password123", "owner123", 
                                False, True, permissions)
            
        self.assertTrue(result)
        
        # Check that encrypt was called with correct parameters
        mock_writer.encrypt.assert_called_once()
        call_args = mock_writer.encrypt.call_args
        
        self.assertEqual(call_args[1]['user_password'], "password123")
        self.assertEqual(call_args[1]['owner_password'], "owner123")
        self.assertTrue(call_args[1]['use_128bit'])
        
    @patch('remove_pdf_password.PdfReader')
    def test_add_password_already_encrypted(self, mock_reader_class):
        """Test adding password to already encrypted PDF."""
        mock_reader = MagicMock()
        mock_reader.is_encrypted = True
        mock_reader_class.return_value = mock_reader
        
        # Mock input to decline re-encryption
        with patch('builtins.input', return_value='n'):
            result = add_password(self.test_pdf, self.output_pdf, "password123", None, False, True)
            
        self.assertFalse(result)
        
    def test_add_password_file_not_found(self):
        """Test password addition with non-existent file."""
        result = add_password("nonexistent.pdf", "output.pdf", "password123", None, False, True)
        self.assertFalse(result)
        
class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios."""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def test_remove_password_file_not_found(self):
        """Test handling when input file doesn't exist."""
        result = remove_password("nonexistent.pdf", "output.pdf", "password", False, True)
        self.assertFalse(result)
        
    def test_remove_password_permission_error(self):
        """Test handling of permission errors."""
        # Create a file we can't read (simulate permission error)
        test_file = os.path.join(self.test_dir, "readonly.pdf")
        with open(test_file, 'wb') as f:
            f.write(b'%PDF-1.4\ntest')
            
        # On Windows, we can't easily create a truly unreadable file
        # So we'll mock the validation to raise PermissionError
        with patch('remove_pdf_password.validate_pdf_file') as mock_validate:
            mock_validate.side_effect = PermissionError("Access denied")
            
            result = remove_password(test_file, "output.pdf", "password", False, True)
            self.assertFalse(result)
            
class TestIntegration(unittest.TestCase):
    """Integration tests that test the full workflow."""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    @patch('remove_pdf_password.PdfReader')
    @patch('remove_pdf_password.PdfWriter')
    def test_full_workflow_with_backup(self, mock_writer_class, mock_reader_class):
        """Test full workflow including backup creation."""
        # Create test PDF
        test_pdf = os.path.join(self.test_dir, "test.pdf")
        with open(test_pdf, 'wb') as f:
            f.write(b'%PDF-1.4\nTest PDF content')
            
        # Mock PDF processing
        mock_reader = MagicMock()
        mock_reader.is_encrypted = True
        mock_reader.decrypt.return_value = True
        mock_reader.pages = [MagicMock()]
        mock_reader_class.return_value = mock_reader
        
        mock_writer = MagicMock()
        mock_writer_class.return_value = mock_writer
        
        output_pdf = os.path.join(self.test_dir, "output.pdf")
        
        with patch('builtins.open', mock_open()):
            result = remove_password(test_pdf, output_pdf, "password", True, True)
            
        self.assertTrue(result)
        
        # Check that backup was created
        backup_files = [f for f in os.listdir(self.test_dir) if "backup" in f]
        self.assertTrue(len(backup_files) > 0)
        
def run_tests():
    """Run all tests."""
    # Disable logging during tests to avoid cluttering output
    import logging
    logging.disable(logging.CRITICAL)
    
    unittest.main(verbosity=2)
    
if __name__ == '__main__':
    run_tests()