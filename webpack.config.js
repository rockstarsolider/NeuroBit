// webpack.config.js
const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const BundleTracker = require('webpack-bundle-tracker');
const CompressionPlugin = require('compression-webpack-plugin');

module.exports = (env, argv) => {
  const isProd = argv.mode === 'production';

  return {
    mode: isProd ? 'production' : 'development',
    devtool: isProd ? false : 'eval-cheap-module-source-map',
    cache: { type: 'filesystem' },
    context: __dirname,
    entry: {
      main: './static/webpack_entry/js/index.js',
      learning_paths: './static/js/learning_paths.js',
      admin_analytics: './static/webpack_entry/js/admin_analytics.js',
      admin_progress_analytics: './static/webpack_entry/js/admin_progress_analytics.js',
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
            options: {
              cacheDirectory: true,
              // (optional) if you want preset-env — safe to leave as-is too
              // presets: [['@babel/preset-env', { targets: 'defaults' }]],
            },
          },
        },
        {
          test: /\.css$/,
          use: [
            MiniCssExtractPlugin.loader, 
            'css-loader', 'postcss-loader',
            {
              loader: 'postcss-loader',
              options: {
                postcssOptions: {
                  plugins: {
                    '@tailwindcss/postcss': {},
                    autoprefixer: {},
                  },
                }
              },
            },
          ],
        },
        {
          test: /\.(woff|woff2|eot|ttf|svg)$/i,
          type: 'asset/resource',
          generator: { filename: 'fonts/[name][ext][query][contenthash:8]' },
        },
      ],
    },
    optimization: {
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          // keep Plotly in its own async chunk; we lazy-load it in the JS
          plotly: { test: /plotly\.js-dist-min/, name: 'plotly', chunks: 'all', priority: 20 },
          vendors: { test: /[\\/]node_modules[\\/]/, name: 'vendors', chunks: 'all', priority: 10 },
        },
      },
      runtimeChunk: { name: 'runtime' },
      minimize: isProd,
    },
    plugins: [
      new MiniCssExtractPlugin({ filename: '[name]-[contenthash].css' }),
      new BundleTracker({ path: __dirname, filename: 'webpack-stats.json' }),
      ...(isProd
        ? [
            new CompressionPlugin({
              algorithm: 'brotliCompress',
              filename: '[path][base].br',
              test: /\.(js|css|svg|woff2?)$/i,
              compressionOptions: { level: 11 },
              threshold: 10 * 1024,
              minRatio: 0.8,
            }),
            new CompressionPlugin({
              algorithm: 'gzip',
              filename: '[path][base].gz',
              test: /\.(js|css|svg|woff2?)$/i,
              threshold: 10 * 1024,
              minRatio: 0.8,
            }),
          ]
        : []),
    ],
    resolve: {
      alias: {
        'maplibre-gl/dist/maplibre-gl.css': false,
      },
    },
    performance: { hints: false },
  };
};
