<?php
/*
Plugin Name: NeuralGPT Browse
Plugin URI: https://github.com/CognitiveCodes/NeuralGPT
Description: A plugin that allows users to browse and search the NeuralGPT repository directly from their WordPress dashboard.
Version: 1.0.0
Author: staszek
Author URI: https://yourwebsite.com
License: GPL2
*/
function neuralgpt_browse_enqueue_scripts() {
    wp_enqueue_style( 'neuralgpt-browse-css', plugin_dir_url( __FILE__ ) . 'assets/neuralgpt-browse.css' );
    wp_enqueue_script( 'neuralgpt-browse-js', plugin_dir_url( __FILE__ ) . 'assets/neuralgpt-browse.js', array( 'jquery' ), '1.0.0', true );
}
add_action( 'wp_enqueue_scripts', 'neuralgpt_browse_enqueue_scripts' );
In the "neuralgpt-browse.php" file, create a new shortcode using the following code:
Copy code

function neuralgpt_browse_shortcode() {
    ob_start();
    include( plugin_dir_path( __FILE__ ) . 'templates/neuralgpt-browse.php' );
    return ob_get_clean();
}
add_shortcode( 'neuralgpt_browse', 'neuralgpt_browse_shortcode' );
function neuralgpt_browse_register_api_routes() {
    register_rest_route( 'neuralgpt-browse/v1', '/search', array(
        'methods' => 'POST',
        'callback' => 'neuralgpt_browse_search'
    ) );
}
add_action( 'rest_api_init', 'neuralgpt_browse_register_api_routes' );
function neuralgpt_browse_search( WP_REST_Request $request ) {
    $searchQuery = $request->get_param( 'search_query' );
    $args = array(
        'post_type' => 'post',
        's' => $searchQuery
    );
    $query = new WP_Query( $args );
    $results = array();
    if ( $query->have_posts() ) {
        while ( $query->have_posts() ) {
            $query->the_post();
            $result = array(
                'title' => get_the_title(),
                'excerpt' => get_the_excerpt(),
                'link' => get_permalink()
            );
            array_push( $results, $result );
        }
    }
    wp_reset_postdata();
    return $results;
}