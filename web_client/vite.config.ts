import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import vuetify from "vite-plugin-vuetify";

export default defineConfig({
  plugins: [
    vue(),
    vuetify({
      autoImport: true
    })
  ],
  base: "./",
  build: {
    outDir: "../outputs",
    emptyOutDir: false
  },
  test: {
    environment: "jsdom",
    globals: true,
    css: false,
    setupFiles: "./src/__tests__/setup.ts",
    deps: {
      inline: ["vuetify"]
    },
    environmentOptions: {
      jsdom: {
        resources: "usable"
      }
    }
  },
  ssr: {
    noExternal: ["vuetify"]
  }
});
