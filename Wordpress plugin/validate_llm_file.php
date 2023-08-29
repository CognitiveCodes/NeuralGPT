<?php
function validate_llm_file($file) {
    $valid_extensions = array('bin'); // List of valid file extensions
    $file_extension = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
    
    if (!in_array($file_extension, $valid_extensions)) {
        return 'Error: Invalid file extension. Please upload a .bin file.';
    }
    
    $file_size = $file['size'];
    $max_size = 1024 * 1024; // Maximum file size (1 MB)
    
    if ($file_size > $max_size) {
        return 'Error: File size exceeds maximum allowed. Please upload a smaller file.';
    }
    
    // Validate LLM file format
    $file_content = file_get_contents($file['tmp_name']);
    $file_header = substr($file_content, 0, 4);
    
    if ($file_header !== 'LLM ') {
        return 'Error: Invalid file format. Please upload a valid LLM file.';
    }
    
    return true; // File is valid
}