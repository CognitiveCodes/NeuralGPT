// Add a new menu item to the WordPress admin dashboard
add_action('admin_menu', 'neuralgpt_add_settings_page');
function neuralgpt_add_settings_page() {
    add_menu_page(
        'NeuralGPT Settings',
        'NeuralGPT',
        'manage_options',
        'neuralgpt-settings',
        'neuralgpt_render_settings_page'
    );
}

// Render the settings page HTML
function neuralgpt_render_settings_page() {
    ?>
    <div class="wrap">
        <h1>NeuralGPT Settings</h1>
        <form method="post" action="options.php">
            <?php settings_fields('neuralgpt-settings-group'); ?>
            <?php do_settings_sections('neuralgpt-settings'); ?>
            <?php submit_button(); ?>
        </form>
    </div>
    <?php
}

// Register the settings fields using the WordPress Settings API
add_action('admin_init', 'neuralgpt_register_settings');
function neuralgpt_register_settings() {
    register_setting('neuralgpt-settings-group', 'neuralgpt_appearance_settings');
    register_setting('neuralgpt-settings-group', 'neuralgpt_behavior_settings');

    add_settings_section(
        'neuralgpt_appearance_section',
        'Appearance Settings',
        'neuralgpt_render_appearance_section',
        'neuralgpt-settings'
    );
    add_settings_section(
        'neuralgpt_behavior_section',
        'Behavior Settings',
        'neuralgpt_render_behavior_section',
        'neuralgpt-settings'
    );

    add_settings_field(
        'neuralgpt_background_color',
        'Background Color',
        'neuralgpt_render_background_color_field',
        'neuralgpt-settings',
        'neuralgpt_appearance_section'
    );

    add_settings_field(
        'neuralgpt_auto_scroll',
        'Auto-Scroll',
        'neuralgpt_render_auto_scroll_field',
        'neuralgpt-settings',
        'neuralgpt_behavior_section'
    );
}

// Render the appearance settings section HTML
function neuralgpt_render_appearance_section() {
    echo '<p>Customize the chat window\'s appearance.</p>';
}

// Render the behavior settings section HTML
function neuralgpt_render_behavior_section() {
    echo '<p>Customize the chat window\'s behavior.</p>';
}

// Render the background color field HTML
function neuralgpt_render_background_color_field() {
    $options = get_option('neuralgpt_appearance_settings');
    $value = isset($options['background_color']) ? $options['background_color'] : '';
    echo '<input type="text" name="neuralgpt_appearance_settings[background_color]" value="' . esc_attr($value) . '" class="color-picker" />';
}

// Render the auto-scroll field HTML
function neuralgpt_render_auto_scroll_field() {
    $options = get_option('neuralgpt_behavior_settings');
    $value = isset($options['auto_scroll']) ? $options['auto_scroll'] : false;
    echo '<label><input type="checkbox" name="neuralgpt_behavior_settings[auto_scroll]" value="1" ' . checked($value, true, false) . ' /> Enable auto-scrolling</label>';
}