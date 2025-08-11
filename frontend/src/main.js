import { createApp } from 'vue';
import App from './App.vue';
import PrimeVue from 'primevue/config';

// PrimeVue styles
import 'primevue/resources/themes/lara-light-blue/theme.css';
import 'primevue/resources/primevue.min.css';
import 'primeicons/primeicons.css';
import 'primeflex/primeflex.css';
import './style.css'; 

const app = createApp(App);
app.use(PrimeVue);
app.mount('#app');