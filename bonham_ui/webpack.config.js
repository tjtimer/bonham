const path = require("path")
const webpack = require("webpack")
const ExtractTextPlugin = require("extract-text-webpack-plugin")

module.exports = {
    entry: {
        // welcome: "./src/welcome.js",
        index: ["babel-polyfill", "./src/index.js"],
        // admin: "./src/admin.js"
    },
    output: {
        path: "/var/www/tjtimer.com/bonham/public/assets/",
        filename: "js/[name].js"
    },
    module: {
        loaders: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                loader: "babel-loader",
            },
            {
                test: /\.scss$/,
                exclude: /node_modules/,
                loader: ExtractTextPlugin.extract({
                    fallback: "style-loader",
                    use: "css-loader!sass-loader!autoprefixer-loader" })
            }
        ]
    },
    plugins: [new ExtractTextPlugin("styles/[name].css"),],
}
