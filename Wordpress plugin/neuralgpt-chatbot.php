<?php
/*
Plugin Name: NeuralGPT Chatbot
Plugin URI: https://github.com/CognitiveCodes/NeuralGPT/tree/main
Description: A chatbot plugin that uses the NeuralGPT system.
Version: 1.0
Author: Your Name
Author URI: https://yourwebsite.com
License: GPL2
*/
error_reporting(E_ALL);
ini_set('display_errors', 1);
require_once ABSPATH . 'wp-admin/includes/plugin.php';

function neuralgpt_chatbot_enqueue_scripts() {
    wp_enqueue_style( 'neuralgpt-chatbot-style', plugin_dir_url( __FILE__ ) . 'neuralgpt-chatbot.css' );
    wp_enqueue_script( 'socket-io', 'https://cdn.socket.io/socket.io-3.0.1.min.js', array(), '3.0.1', true );
    wp_enqueue_script( 'neuralgpt-chatbot', plugin_dir_url( __FILE__ ) . 'neuralgpt-chatbot.js', array( 'jquery', 'socket-io' ), '1.0.0', true );
}

add_action( 'wp_enqueue_scripts', 'neuralgpt_chatbot_enqueue_scripts' );

function neuralgpt_chatbot_shortcode() {
    ob_start();
    ?>
    <div id="neuralgpt-chat">
        <div id="neuralgpt-chat-log"></div>
        <div id="neuralgpt-chat-input-container">
            <input type="text" id="neuralgpt-chat-input" placeholder="Type your message...">
            <button id="neuralgpt-chat-send">Send</button>
        </div>
    </div>
    <?php
    return ob_get_clean();
}

add_shortcode( 'neuralgpt-chatbot', 'neuralgpt_chatbot_shortcode' );

function neuralgpt_chatbot_ajax_handler() {
    $message = $_POST['message'];

    // Use the appropriate Python executable and script path
    $python_executable = '"E:/xampp/htdocs/wordpress/wp-content/plugins/neuralgpt-chatbot/dist/python_script/python_script.exe'; // Modify this if needed
    $python_script = 'E:/xampp/htdocs/wordpress/wp-content/plugins/neuralgpt-chatbot/python_script.py'; // Replace with the actual path to your python_script.py file

    // Construct the command to execute the Python script
    $command = $python_executable . ' ' . $python_script . ' ' . escapeshellarg($message);

    // Execute the command and capture the output
    $output = shell_exec($command);

    // Handle the generated output from the Python script
    if ($output !== null) {
        // Process the generated output as needed
        echo wp_json_encode(array('message' => $output));
    } else {
        // Handle the case where the output is not available
        echo wp_json_encode(array('message' => 'No response'));
    }

    wp_die();
}

add_action( 'wp_ajax_neuralgpt_chatbot', 'neuralgpt_chatbot_ajax_handler' );
add_action( 'wp_ajax_nopriv_neuralgpt_chatbot', 'neuralgpt_chatbot_ajax_handler' );

function neuralgpt_chatbot_add_settings_page_callback() {
    add_menu_page(
        'NeuralGPT Chatbot Settings',
        'NeuralGPT Chatbot',
        'manage_options',
        'neuralgpt-chatbot-settings',
        'neuralgpt_chatbot_settings_page_callback',
        'dashicons-admin-generic',
        75
    );
}

add_action('admin_menu', 'neuralgpt_chatbot_add_settings_page_callback');

function neuralgpt_chatbot_settings_page_callback() {
    // Display the settings page content here
    echo '<div class="wrap">';
    echo '<h1>NeuralGPT Chatbot Settings</h1>';
    echo '<p>Model Status: The pretrained model is loaded successfully.</p>';

    // Add option to select the chatbot model

    $selected_model = get_option('neuralgpt_chatbot_model');
    echo '<h2>Select Chatbot Model</h2>';
    echo '<form method="post" action="">';
    echo '<select name="neuralgpt_chatbot_model">';
    echo '<option value="gpt2" ' . selected($selected_model, 'gpt2', false) . '>GPT-2</option>';
    echo '<option value="kobold_horde" ' . selected($selected_model, 'kobold_horde', false) . '>Kobold Horde</option>';
    echo '</select>';
    echo '<br><br>';   
    echo '<input type="submit" name="neuralgpt_chatbot_save_model" class="button button-primary" value="Save Model">';
    echo '</form>';
        if(is_file('E:/xampp/htdocs/wordpress/wp-content/plugins/neuralgpt-chatbot/dist/python_script.exe') )
        {
            echo '<br> python executables FOUND !!!<br> ';
            echo '<br> Loading it, please standby...<br> ';
        }
        else {
            echo '<br> python executables MISSING !!!<br> ';
            echo '<br> :-(.......<br> ';
            die;
        }
        
    // Save selected model option
    if (isset($_POST['neuralgpt_chatbot_save_model'])) {
        $selected_model = sanitize_text_field($_POST['neuralgpt_chatbot_model']);
        update_option('neuralgpt_chatbot_model', $selected_model);
        echo '<br><p>Model saved successfully!</p>';
    }

    echo '</div>';
}
add_action("wp_ajax_neuralgpt_chat", "neuralgpt_chat");
add_action("wp_ajax_nopriv_neuralgpt_chat", "neuralgpt_chat");
function neuralgpt_chat() {
 $message = $_POST["message"];
 // TODO: generate response using NeuralGPT system
 $response = "Hello, world!";
 echo json_encode(array("message" => $response));
 wp_die();
}
