import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import "./styles/tailwind.css";
import "./styles/main.css";

const app = createApp(App);

// 注册路由
app.use(router);

app.mount("#app");
