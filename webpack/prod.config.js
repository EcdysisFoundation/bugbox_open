const { merge } = require('webpack-merge');
const commonConfig = require('./common.config');

// This is if using S3
// This variable should mirror the one from config/settings/production.py
///const staticUrl = `https://ecdysis-static.s3.amazonaws.com/`;

// This is to use local storage
const staticUrl = '/static/';

module.exports = merge(commonConfig, {
  mode: 'production',
  devtool: 'source-map',
  bail: true,
  output: {
    publicPath: `${staticUrl}webpack_bundles/`,
  },
});
