const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
  target: 'web',
  context: path.join(__dirname, '../'),
  entry: {
    project: path.resolve(__dirname, '../bugbox3/static/js/project'),
    vendors: path.resolve(__dirname, '../bugbox3/static/js/vendors'),
    jquery_tools: path.resolve(__dirname, '../bugbox3/static/js/jquery_tools'),
    morphospecies: path.resolve(__dirname, '../bugbox3/static/js/morphospecies'),
    morphospecies_combine: path.resolve(__dirname, '../bugbox3/static/js/morphospecies_combine'),
    morphospecies_select: path.resolve(__dirname, '../bugbox3/static/js/morphospecies_select'),
    multi_specimens: path.resolve(__dirname, '../bugbox3/static/js/multi_specimens'),
    experiments: path.resolve(__dirname, '../bugbox3/static/js/experiments'),
    samples: path.resolve(__dirname, '../bugbox3/static/js/samples'),
    sample_detail: path.resolve(__dirname, '../bugbox3/static/js/sample_detail'),
    apexcharts_config: path.resolve(__dirname, '../bugbox3/static/js/apexcharts_config'),
    gbif_api: path.resolve(__dirname, '../bugbox3/static/js/gbif_api'),
    specimens_all: path.resolve(__dirname, '../bugbox3/static/js/specimens_all'),
    timeline: path.resolve(__dirname, '../bugbox3/static/js/timeline'),
    collections: path.resolve(__dirname, '../bugbox3/static/js/collections'),
    stitcher: path.resolve(__dirname, '../bugbox3/static/js/stitcher'),
    stitcher_form: path.resolve(__dirname, '../bugbox3/static/js/stitcher_form'),
    site_form: path.resolve(__dirname, '../bugbox3/static/js/site_form'),

  },
  output: {
    path: path.resolve(
      __dirname,
      '../bugbox3/static/webpack_bundles/',
    ),
    publicPath: '/static/webpack_bundles/',
    filename: 'js/[name]-[fullhash].js',
    chunkFilename: 'js/[name]-[hash].js',
  },
  plugins: [
    new BundleTracker({
      path: path.resolve(path.join(__dirname, '../')),
      filename: 'webpack-stats.json',
    }),
    new MiniCssExtractPlugin({ filename: 'css/[name].[contenthash].css' }),
  ],
  module: {
    rules: [
      // we pass the output from babel loader to react-hot loader
      {
        test: /\.js$/,
        loader: 'babel-loader',
      },
      {
        test: /\.s?css$/i,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          {
            loader: 'postcss-loader',
            options: {
              postcssOptions: {
                plugins: ['postcss-preset-env', 'autoprefixer', 'pixrem'],
              },
            },
          },
          'sass-loader',
        ],
      },
    ],
  },
  resolve: {
    modules: ['node_modules'],
    extensions: ['.js', '.jsx'],
  },
  watchOptions: {
    ignored: [path.resolve(__dirname, '../bugbox3/node_modules'),]
  },
};
