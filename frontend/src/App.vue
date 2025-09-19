<template>
  <div id="app">
    <h1>Episode Renamer</h1>
    <form @submit.prevent="submitRename" class="form-container">
      <div>
        <label>Serie:</label>
        <input v-model="form.series" type="text" required />
      </div>
      <div>
        <label>Staffel:</label>
        <input v-model.number="form.season" type="number" min="1" required />
      </div>
      <div>
        <label>Verzeichnis:</label>
        <select v-model="form.directory" required>
          <option v-for="dir in directories" :key="dir" :value="dir">{{ dir }}</option>
        </select>
        <button type="button" @click="fetchDirectories">Verzeichnisse neu laden</button>
      </div>
      <div>
        <label>Sprache:</label>
        <select v-model="form.lang">
          <option value="de">Deutsch</option>
          <option value="en">Englisch</option>
        </select>
      </div>
      <div>
        <label>--dry-run</label>
        <input v-model="form.dry_run" type="checkbox" />
      </div>
      <div>
        <label>--assign-seq</label>
        <input v-model="form.assign_seq" type="checkbox" />
      </div>
      <div>
        <label>Match Threshold:</label>
        <input v-model.number="form.threshold" type="number" step="0.01" min="0" max="1" />
      </div>
      <div class="submit-container">
        <button type="submit">Umbenennen</button>
      </div>
    </form>

    <div v-if="log.length" class="log-container">
      <h3>Log</h3>
      <pre>{{ log.join('\n') }}</pre>
    </div>

    <div v-if="error" class="error-container">
      <strong>Fehler:</strong> {{ error }}
    </div>
  </div>
</template>

<script>
export default {
  name: "App",
  data() {
    return {
      directories: [],
      form: {
        series: '',
        season: 1,
        directory: '',
        dry_run: true,
        assign_seq: false,
        threshold: 0.6,
        lang: 'de'
      },
      log: [],
      error: ''
    };
  },
  methods: {
    fetchDirectories() {
      fetch("http://localhost:3333/directories")
        .then(response => response.json())
        .then(data => {
          this.directories = data.directories;
        })
        .catch(() => {
          this.error = "Fehler beim Laden der Verzeichnisse";
        });
    },
    submitRename() {
      this.log = [];
      this.error = '';
      const formData = new FormData();
      for (const field in this.form) {
        formData.append(field, this.form[field]);
      }
      fetch("http://localhost:3333/rename", {
        method: "POST",
        body: formData
      })
        .then(response => response.json())
        .then(data => {
          if (data.error) this.error = data.error;
          this.log = data.log || [];
          if (data.directories) this.directories = data.directories;
        })
        .catch(() => {
          this.error = "Fehler beim Umbenennen.";
        });
    }
  },
  mounted() {
    this.fetchDirectories();
  }
};
</script>
