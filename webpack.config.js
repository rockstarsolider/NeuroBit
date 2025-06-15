const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const BundleTracker = require('webpack-bundle-tracker');

module.exports = {
    mode: 'production',
    devtool: false,
    context: __dirname,
    entry: {
        main: './static/webpack_entry/js/index.js',
    },
    output: {
        path: path.resolve('./static/webpack_output/'),
        filename: '[name]-[contenthash].js',
        publicPath: '/static/webpack_output/',
        clean: true,
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                },
            },
            {
                test: /\.css$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    'css-loader',
                    'postcss-loader',
                ],
            },
            {
                test: /\.(woff|woff2|eot|ttf|svg)$/i,
                type: 'asset/resource',
                generator: {
                    filename: 'fonts/[name][ext][query][contenthash:8]',
                },
            },
        ],
    },
    optimization: {
        splitChunks: { // Separate vendor libraries for better caching
            cacheGroups: {
                vendor: {
                    test: /[\\/]node_modules[\\/]/,
                    name: 'vendors',
                    chunks: 'all',
                },
            },
        },
    },
    plugins: [
        new MiniCssExtractPlugin({
            filename: '[name]-[contenthash].css',
        }),
        new BundleTracker({
            path: __dirname,
            filename: 'webpack-stats.json',
        }),
    ],
};