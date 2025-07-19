const API_BASE_URL = "http://localhost:8000";
async function getBodies() {
  try {
    const response = await fetch(`${API_BASE_URL}/bodies`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const result = await response.json();
    return result.data || result;
  } catch (error) {
    console.error("Error fetching celestial bodies:", error);
    throw new Error(`Failed to fetch celestial bodies: ${error instanceof Error ? error.message : "Unknown error"}`);
  }
}
const load = async () => {
  try {
    const bodies = await getBodies();
    return {
      bodies
    };
  } catch (error) {
    console.error("Failed to load celestial bodies:", error);
    return {
      bodies: [],
      error: error instanceof Error ? error.message : "Failed to load data"
    };
  }
};

var _page_ts = /*#__PURE__*/Object.freeze({
  __proto__: null,
  load: load
});

const index = 2;
let component_cache;
const component = async () => component_cache ??= (await import('./_page.svelte-CvC7BuM1.js')).default;
const universal_id = "src/routes/+page.ts";
const imports = ["_app/immutable/nodes/2.CdKjAr_O.js","_app/immutable/chunks/-cg1m2IV.js","_app/immutable/chunks/CpDTQf_-.js","_app/immutable/chunks/D6YF6ztN.js","_app/immutable/chunks/BCregXEj.js"];
const stylesheets = [];
const fonts = [];

export { component, fonts, imports, index, stylesheets, _page_ts as universal, universal_id };
//# sourceMappingURL=2-OqeIyMMj.js.map
