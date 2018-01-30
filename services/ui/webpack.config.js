//          'css-loader?modules&camelCase&importLoaders=1&localIdentName=[name]__[local]___[hash:base64:5]'

module.exports = {
	entry: "./src/app.js",
	output: {
		filename: "index.js"
	},
	module: {
		loaders: [
			{
				test: /\.js$/,
				exclude: /node_modules/,
				loader: 'babel-loader',
				query: {
					presets: ['es2015', 'react']
				}
			},
			{
        test: /\.json$/,
        loader: 'json-loader'
      },

			// {
      //   test: /react-table.css$/,
			// 	  loaders: [
	    //       'style-loader',
	    //       'css-loader'
	    //     ]
      // },
			// {
      //   test: /^((?!react-table).)*\.css/,
      //   loaders: [
      //     'style-loader',
      //     'css-loader?modules&camelCase&importLoaders=1&localIdentName=[name]__[local]___[hash:base64:5]'
      //   ]
      // },
			{
        test: /\.css$/,
        loaders: [
          'style-loader',
          'css-loader'
        ]
      },
			{
        test: /\.svg$/,
        loader: 'url-loader'
      }
		]
	}
};
