const webpack = require('webpack');
const {VueLoaderPlugin} = require('vue-loader')
const path = require(`path`);

module.exports = (env, argv) => ({
    name: 'paladin-ui',
    mode: argv.mode || 'development',
    entry: './src/main.ts',
    devtool: argv.mode !== 'production' ? "source-map" : undefined,
    stats: {
        hash: false, version: false, modules: false  // reduce verbosity
    },
    output: {
        filename: 'index.js',
        path: `${__dirname}/static`
    },
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                loader: 'ts-loader',
                options: {
                    appendTsSuffixTo: [/\.vue$/],
                    allowTsInNodeModules: true
                }

            },
            {
                test: /\.css$/i,
                use: ['style-loader', 'css-loader'],
            },
            {
                test: /\.scss$/i,  /* Vue.js has some */
                use: ['style-loader', 'css-loader', 'sass-loader'],
            },
            {
                test: /\.(png|jpe?g|gif|svg)$/i,
                type: 'asset/resource',
                generator: {
                    filename: 'img/[hash][ext][query]'
                }
            },
            {
                test: /\.vue$/,
                use: 'vue-loader'
            }
        ],
    },
    resolve: {
        extensions: ['.*', '.js', '.jsx', '.vue', '.ts', '.tsx'],
        symlinks: false,
        alias: {
            vue: path.resolve(`node_modules/vue/dist/vue.esm-bundler.js`),
            infra: path.resolve(`src/infra`)
        },
    },
    externals: {
        fs: '{}'
    },
    plugins: [new VueLoaderPlugin(),
        new webpack.DefinePlugin({
            'process': {browser: true, env: {}},
            __VUE_OPTIONS_API__: true,
            __VUE_PROD_DEVTOOLS__: true
        }),
        new webpack.ProvidePlugin({'Buffer': 'buffer'}),
        new webpack.DefinePlugin({
            '__VUE_PROD_HYDRATION_MISMATCH_DETAILS__': JSON.stringify(false)
        })
    ]
});
