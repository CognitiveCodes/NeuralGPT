<?php
function neuralgpt_chatbot_register_settings() {
    add_settings_section( 'neuralgpt_settings_section', 'NeuralGPT Settings', '', 'neuralgpt_settings' );
    add_settings_field( 'pretrained_llm_path', 'Pretrained LLM Path', 'neuralgpt_chatbot_pretrained_llm_path_callback', 'neuralgpt_settings', 'neuralgpt_settings_section' );
    register_setting( 'neuralgpt_settings', 'pretrained_llm_path', 'sanitize_text_field' );
}

function neuralgpt_chatbot_pretrained_llm_path_callback() {
    $pretrained_llm_path = get_option( 'pretrained_llm_path' );
    ?>
    <input type="text" id="pretrained_llm_path" name="pretrained_llm_path" value="<?php echo esc_attr( $pretrained_llm_path ); ?>">
    <?php
}

add_action( 'admin_init', 'neuralgpt_chatbot_register_settings' );

function neuralgpt_chatbot_settings_page() {
    ?>
    <div class="wrap">
        <h1>NeuralGPT Chatbot Settings</h1>
        <form method="post" action="options.php">
            <?php settings_fields( 'neuralgpt_settings' ); ?>
            <?php do_settings_sections( 'neuralgpt_settings' ); ?>
            <?php submit_button(); ?>
        </form>
    </div>
    <?php
}

add_action( 'admin_menu', function() {
    add_options_page( 'NeuralGPT Chatbot Settings', 'NeuralGPT Chatbot', 'manage_options', 'neuralgpt_settings', 'neuralgpt_chatbot_settings_page' );
} );