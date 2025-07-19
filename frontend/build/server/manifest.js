const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set(["favicon.png"]),
	mimeTypes: {".png":"image/png"},
	_: {
		client: {start:"_app/immutable/entry/start.BtXsNNHF.js",app:"_app/immutable/entry/app.BXvUpSkm.js",imports:["_app/immutable/entry/start.BtXsNNHF.js","_app/immutable/chunks/iEKTm3aT.js","_app/immutable/chunks/-cg1m2IV.js","_app/immutable/chunks/BCregXEj.js","_app/immutable/entry/app.BXvUpSkm.js","_app/immutable/chunks/-cg1m2IV.js","_app/immutable/chunks/CpDTQf_-.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./chunks/0-Cn4ZhDvK.js')),
			__memo(() => import('./chunks/1-s5EiBWs_.js')),
			__memo(() => import('./chunks/2-OqeIyMMj.js')),
			__memo(() => import('./chunks/3-CIEURWS5.js')),
			__memo(() => import('./chunks/4-DsaEykSc.js'))
		],
		routes: [
			{
				id: "/",
				pattern: /^\/$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 2 },
				endpoint: null
			},
			{
				id: "/3d",
				pattern: /^\/3d\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 3 },
				endpoint: null
			},
			{
				id: "/dashboard",
				pattern: /^\/dashboard\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 4 },
				endpoint: null
			}
		],
		prerendered_routes: new Set([]),
		matchers: async () => {
			
			return {  };
		},
		server_assets: {}
	}
}
})();

const prerendered = new Set([]);

export { manifest, prerendered };
//# sourceMappingURL=manifest.js.map
