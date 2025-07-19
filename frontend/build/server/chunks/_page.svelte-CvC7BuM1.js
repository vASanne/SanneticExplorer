import { c as create_ssr_component, v as validate_component, e as escape, o as onDestroy, b as each, a as subscribe, d as add_attribute, f as createEventDispatcher } from './ssr-BNMWNNGj.js';
import { w as writable } from './index-DiWYjFJh.js';

const SolarSystemCanvas = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { celestialBodies = [] } = $$props;
  let { showOrbits = true } = $$props;
  let { showLabels = true } = $$props;
  let { autoRotate = false } = $$props;
  let { cameraSpeed = 1 } = $$props;
  if ($$props.celestialBodies === void 0 && $$bindings.celestialBodies && celestialBodies !== void 0) $$bindings.celestialBodies(celestialBodies);
  if ($$props.showOrbits === void 0 && $$bindings.showOrbits && showOrbits !== void 0) $$bindings.showOrbits(showOrbits);
  if ($$props.showLabels === void 0 && $$bindings.showLabels && showLabels !== void 0) $$bindings.showLabels(showLabels);
  if ($$props.autoRotate === void 0 && $$bindings.autoRotate && autoRotate !== void 0) $$bindings.autoRotate(autoRotate);
  if ($$props.cameraSpeed === void 0 && $$bindings.cameraSpeed && cameraSpeed !== void 0) $$bindings.cameraSpeed(cameraSpeed);
  return `<div class="w-full h-full bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 flex items-center justify-center rounded-lg relative overflow-hidden"> <div class="absolute inset-0 opacity-30">${each(Array(50), (_, i) => {
    return `<div class="absolute w-1 h-1 bg-white rounded-full animate-pulse" style="${"left: " + escape(Math.random() * 100, true) + "%; top: " + escape(Math.random() * 100, true) + "%; animation-delay: " + escape(Math.random() * 3, true) + "s"}"></div>`;
  })}</div> <div class="text-center text-white z-10"><div class="text-6xl mb-4" data-svelte-h="svelte-1jkn3jr">🌌</div> <h2 class="text-3xl font-bold mb-4" data-svelte-h="svelte-apm1ds">Solar System Explorer</h2> <p class="text-lg mb-6 text-white/80" data-svelte-h="svelte-1trxmyn">Interactive 3D visualization coming soon...</p> <div class="grid grid-cols-2 gap-4 mb-6 text-sm"><div class="bg-white/10 rounded-lg p-3"><div class="font-bold" data-svelte-h="svelte-pb9ca8">Show Orbits</div> <div class="text-white/70">${escape(showOrbits ? "Enabled" : "Disabled")}</div></div> <div class="bg-white/10 rounded-lg p-3"><div class="font-bold" data-svelte-h="svelte-1a9lziy">Show Labels</div> <div class="text-white/70">${escape(showLabels ? "Enabled" : "Disabled")}</div></div> <div class="bg-white/10 rounded-lg p-3"><div class="font-bold" data-svelte-h="svelte-rchvf0">Auto Rotate</div> <div class="text-white/70">${escape(autoRotate ? "Enabled" : "Disabled")}</div></div> <div class="bg-white/10 rounded-lg p-3"><div class="font-bold" data-svelte-h="svelte-1ocmuto">Camera Speed</div> <div class="text-white/70">${escape(cameraSpeed)}x</div></div></div> <div class="loading loading-spinner loading-lg"></div></div></div>`;
});
const SpeedControl = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let currentSpeed;
  let $speedFactor, $$unsubscribe_speedFactor;
  const speedFactor = writable(1);
  $$unsubscribe_speedFactor = subscribe(speedFactor, (value) => $speedFactor = value);
  const speedOptions = [
    { label: "Pause", value: 0 },
    { label: "0.1x", value: 0.1 },
    { label: "0.5x", value: 0.5 },
    { label: "1x", value: 1 },
    { label: "2x", value: 2 },
    { label: "5x", value: 5 },
    { label: "10x", value: 10 }
  ];
  if ($$props.speedFactor === void 0 && $$bindings.speedFactor && speedFactor !== void 0) $$bindings.speedFactor(speedFactor);
  currentSpeed = $speedFactor;
  $$unsubscribe_speedFactor();
  return `<div class="speed-control bg-base-200 p-4 rounded-lg"><h3 class="text-lg font-semibold mb-3" data-svelte-h="svelte-f44e1u">Simulation Speed</h3>  <div class="flex flex-wrap gap-2 mb-3">${each(speedOptions, (option) => {
    return `<button class="${"btn btn-sm " + escape(
      currentSpeed === option.value ? "btn-primary" : "btn-outline",
      true
    )}">${escape(option.label)} </button>`;
  })}</div>  <div class="form-control"><label class="label"><span class="label-text">Custom Speed: ${escape(currentSpeed.toFixed(1))}x</span></label> <input type="range" min="0" max="20" step="0.1" class="range range-primary"${add_attribute("value", currentSpeed, 0)}> <div class="flex justify-between text-xs text-base-content/70" data-svelte-h="svelte-1rh7ick"><span>0x</span> <span>10x</span> <span>20x</span></div></div>  <div class="text-sm text-base-content/70 mt-2">${currentSpeed === 0 ? `<span class="text-warning" data-svelte-h="svelte-13j51dw">Simulation paused</span>` : `${currentSpeed < 1 ? `<span class="text-info" data-svelte-h="svelte-d5bwas">Slow motion</span>` : `${currentSpeed > 1 ? `<span class="text-success" data-svelte-h="svelte-gltbjn">Fast forward</span>` : `<span class="text-success" data-svelte-h="svelte-1lnsad6">Normal speed</span>`}`}`}</div></div>`;
});
function getBodyColor(body) {
  switch (body.body_type?.toLowerCase()) {
    case "star":
      return "#ffff00";
    case "planet":
      switch (body.name?.toLowerCase()) {
        case "mercury":
          return "#8c7853";
        case "venus":
          return "#e7cdcd";
        case "earth":
          return "#6b93d6";
        case "mars":
          return "#c1440e";
        case "jupiter":
          return "#d8ca9d";
        case "saturn":
          return "#fad5a5";
        case "uranus":
          return "#d1e7e7";
        case "neptune":
          return "#5b5ddf";
        default:
          return "#aaaaaa";
      }
    case "moon":
      return "#c0c0c0";
    case "satellite":
      return "#ff6b35";
    default:
      return "#aaaaaa";
  }
}
function formatDistance(km) {
  if (km >= 1e6) {
    return `${(km / 1e6).toFixed(2)}M km`;
  } else if (km >= 1e3) {
    return `${(km / 1e3).toFixed(2)}k km`;
  }
  return `${km.toFixed(2)} km`;
}
const OrbitSidePanel = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let groupedBodies;
  let { bodies = [] } = $$props;
  let { isOpen = false } = $$props;
  createEventDispatcher();
  if ($$props.bodies === void 0 && $$bindings.bodies && bodies !== void 0) $$bindings.bodies(bodies);
  if ($$props.isOpen === void 0 && $$bindings.isOpen && isOpen !== void 0) $$bindings.isOpen(isOpen);
  groupedBodies = bodies.reduce(
    (groups, body) => {
      const type = body.body_type || "Unknown";
      if (!groups[type]) {
        groups[type] = [];
      }
      groups[type].push(body);
      return groups;
    },
    {}
  );
  return ` <div class="${"fixed top-0 right-0 h-full w-80 bg-base-100 shadow-xl transform transition-transform duration-300 ease-in-out " + escape(isOpen ? "translate-x-0" : "translate-x-full", true) + " z-50"}"><div class="h-full flex flex-col"> <div class="p-4 border-b border-base-300"><div class="flex justify-between items-center"><h2 class="text-xl font-bold" data-svelte-h="svelte-17l4g1q">Celestial Bodies</h2> <button class="btn btn-ghost btn-sm" data-svelte-h="svelte-1tx4pti"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg></button></div> <p class="text-sm text-base-content/70 mt-1">${escape(bodies.length)} bodies loaded</p></div>  <div class="flex-1 overflow-y-auto p-4 space-y-4">${each(Object.entries(groupedBodies), ([type, typeBodies]) => {
    return `<div class="card bg-base-200 shadow-sm"><div class="card-body p-4"><h3 class="card-title text-lg capitalize">${escape(type)}</h3> <div class="space-y-2">${each(typeBodies, (body) => {
      return `<div class="flex items-center justify-between p-2 bg-base-100 rounded-lg hover:bg-base-300 transition-colors"><div class="flex items-center space-x-3 flex-1"> <div class="w-4 h-4 rounded-full border border-base-300" style="${"background-color: " + escape(getBodyColor(body), true)}"></div>  <div class="flex-1 min-w-0"><div class="font-medium truncate">${escape(body.name)}</div> <div class="text-xs text-base-content/70">${escape(formatDistance(body.radius_km || 0))} • ${escape(formatDistance((body.mean_distance_au || 0) * 1495978707e-1))}</div> </div></div>  <div class="flex space-x-1"><button class="btn btn-ghost btn-xs" title="Center camera" data-svelte-h="svelte-17uyfh"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg></button> <button class="btn btn-ghost btn-xs" title="Edit properties" data-svelte-h="svelte-1ea0gem"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg> </button></div> </div>`;
    })} </div></div> </div>`;
  })}</div>  ${``}</div></div>  ${isOpen ? `<div class="fixed inset-0 bg-black bg-opacity-50 z-40"></div>` : ``}`;
});
const PerformanceMonitor = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { isVisible = false } = $$props;
  let fps = 0;
  onDestroy(() => {
  });
  if ($$props.isVisible === void 0 && $$bindings.isVisible && isVisible !== void 0) $$bindings.isVisible(isVisible);
  return `${isVisible ? `<div class="fixed top-4 left-4 bg-base-200 p-3 rounded-lg shadow-lg z-50"><div class="text-sm font-mono"><div class="flex items-center space-x-2"><span class="text-base-content/70" data-svelte-h="svelte-7bhoz1">FPS:</span> <span class="${"font-bold " + escape(
    "text-error",
    true
  )}">${escape(fps)}</span></div> <div class="text-xs text-base-content/50 mt-1" data-svelte-h="svelte-1nq2679">Target: 60 FPS</div></div></div>` : ``}`;
});
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let bodies;
  let error;
  let { data } = $$props;
  let isSidePanelOpen = false;
  let showPerformanceMonitor = false;
  if ($$props.data === void 0 && $$bindings.data && data !== void 0) $$bindings.data(data);
  bodies = data.bodies || [];
  error = data.error;
  return `${$$result.head += `<!-- HEAD_svelte-tws31o_START -->${$$result.title = `<title>Sannetic Explorer</title>`, ""}<meta name="description" content="Solar System Exploration Dashboard"><!-- HEAD_svelte-tws31o_END -->`, ""}  <nav class="navbar bg-base-100 shadow-lg" data-svelte-h="svelte-92s0hv"><div class="navbar-start"><div class="dropdown"><label tabindex="0" class="btn btn-ghost lg:hidden"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg></label> <ul tabindex="0" class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52"><li><a href="/">Home</a></li> <li><a href="/3d">3D View</a></li> <li><a href="/dashboard">Dashboard</a></li></ul></div> <a href="/" class="btn btn-ghost text-xl">Sannetic Explorer</a></div> <div class="navbar-center hidden lg:flex"><ul class="menu menu-horizontal px-1"><li><a href="/">Home</a></li> <li><a href="/3d">3D View</a></li> <li><a href="/dashboard">Dashboard</a></li></ul></div> <div class="navbar-end"><div class="dropdown dropdown-end"><label tabindex="0" class="btn btn-circle btn-ghost"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zM21 5a2 2 0 00-2-2h-4a2 2 0 00-2 2v12a4 4 0 004 4h4a2 2 0 002-2V5z"></path></svg></label> <ul tabindex="0" class="dropdown-content menu p-2 shadow bg-base-100 rounded-box w-52"><li><a data-set-theme="light">Light</a></li> <li><a data-set-theme="dark">Dark</a></li> <li><a data-set-theme="cyberpunk">Cyberpunk</a></li> <li><a data-set-theme="synthwave">Synthwave</a></li></ul></div></div></nav>  ${validate_component(PerformanceMonitor, "PerformanceMonitor").$$render($$result, { isVisible: showPerformanceMonitor }, {}, {})} <div class="hero min-h-screen bg-gradient-to-br from-base-200 to-base-300" data-svelte-h="svelte-k1e99d"><div class="hero-content text-center"><div class="max-w-md"><h1 class="text-5xl font-bold text-primary">Sannetic Explorer</h1> <p class="py-6 text-base-content">Explore the solar system with real-time data and 3D visualizations</p> <div class="flex gap-4 justify-center"><a href="/3d" class="btn btn-primary">3D Solar System</a> <a href="/dashboard" class="btn btn-outline">System Dashboard</a></div></div></div></div>  <div class="container mx-auto px-4 py-8"><div class="grid grid-cols-1 lg:grid-cols-4 gap-6"> <div class="lg:col-span-3"><div class="card bg-base-100 shadow-xl"><div class="card-body"><div class="flex justify-between items-center mb-4"><h2 class="card-title text-2xl" data-svelte-h="svelte-l26vif">Live Solar System View</h2> <div class="flex gap-2"><button class="btn btn-ghost btn-sm" title="Toggle performance monitor" data-svelte-h="svelte-1l6bsva"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg></button> <button class="btn btn-outline btn-sm"><svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg> ${escape("Show")} Bodies</button></div></div> <p class="text-base-content/70 mb-6" data-svelte-h="svelte-ix41wc">Interactive 3D visualization of the solar system. Use your mouse to rotate, zoom, and explore.</p> ${error ? `<div class="alert alert-error mb-4"><svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg> <span>Error loading celestial data: ${escape(error)}</span></div>` : ``} <div class="w-full h-96 bg-base-300 rounded-lg overflow-hidden">${validate_component(SolarSystemCanvas, "SolarSystemCanvas").$$render($$result, { bodies, width: 800, height: 400 }, {}, {})}</div> ${bodies.length > 0 ? `<div class="mt-4 text-sm text-base-content/70">Loaded ${escape(bodies.length)} celestial bodies from the database</div>` : ``}</div></div></div>  <div class="lg:col-span-1">${validate_component(SpeedControl, "SpeedControl").$$render($$result, {}, {}, {})}</div></div></div>  ${validate_component(OrbitSidePanel, "OrbitSidePanel").$$render($$result, { bodies, isOpen: isSidePanelOpen }, {}, {})} <div class="container mx-auto px-4 py-8" data-svelte-h="svelte-1ehb1ht"><div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"><div class="card bg-base-100 shadow-xl"><div class="card-body"><h2 class="card-title">Planets</h2> <p>Explore the eight planets of our solar system</p> <div class="card-actions justify-end"><button class="btn btn-primary">View</button></div></div></div> <div class="card bg-base-100 shadow-xl"><div class="card-body"><h2 class="card-title">Moons</h2> <p>Discover natural satellites and their characteristics</p> <div class="card-actions justify-end"><button class="btn btn-primary">View</button></div></div></div> <div class="card bg-base-100 shadow-xl"><div class="card-body"><h2 class="card-title">Spacecraft</h2> <p>Track missions and exploration data</p> <div class="card-actions justify-end"><button class="btn btn-primary">View</button></div></div></div></div></div>`;
});

export { Page as default };
//# sourceMappingURL=_page.svelte-CvC7BuM1.js.map
