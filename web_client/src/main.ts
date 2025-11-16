import { createApp } from "vue";
import App from "./App.vue";
import "./style.css";

import "vuetify/styles";
import "@mdi/font/css/materialdesignicons.css";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

const vuetify = createVuetify({
  components,
  directives,
  defaults: {
    VTextField: { variant: "outlined", density: "comfortable" },
    VSelect: { variant: "outlined", density: "comfortable" },
    VBtn: { rounded: "lg" },
    VCard: { rounded: "xl" }
  },
  theme: {
    defaultTheme: "light",
    themes: {
      light: {
        colors: {
          primary: "#5d5fef",
          secondary: "#6c6f80",
          surface: "#ffffff",
          background: "#eef1f7"
        }
      }
    }
  }
});

createApp(App).use(vuetify).mount("#app");
