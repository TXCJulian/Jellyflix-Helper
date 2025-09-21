<template>
  <div id="app" class="app">
    <h1>Episode Renamer</h1>

    <form @submit.prevent="submitRename" class="form-container">
      <div>
        <label class="label_serie" for="series">Serie:</label>
        <input id="series" v-model="form.series" type="text" placeholder="Name der Serie" required />
      </div>

      <div>
        <label for="season">Staffel:</label>
        <input id="season" v-model.number="form.season" type="number" min="1" required />
      </div>

      <div>
        <label for="directory">Verzeichnis:</label>
        <select id="directory" v-model="form.directory" :disabled="isLoadingDirs || isRenaming" required>
          <option v-for="dir in directories" :key="dir" :value="dir">
            {{ dir }}
          </option>
        </select>

        <button type="button" @click="refreshDirectories" :disabled="isLoadingDirs || isRenaming" class="btn-refresh">
          <span v-if="isLoadingDirs" class="loader-sm"></span>
          <span v-else>Verzeichnisse neu laden</span>
        </button>
      </div>

      <div>
        <label for="lang">Sprache:</label>
        <select id="lang" v-model="form.lang">
          <option value="de">Deutsch</option>
          <option value="en">Englisch</option>
        </select>
      </div>

      <div class="checkbox-group">
        <input id="dry_run" v-model="form.dry_run" type="checkbox" />
        <label for="dry_run">--dry-run</label>
      </div>
      <div class="checkbox-group">
        <input id="assign_seq" v-model="form.assign_seq" type="checkbox" />
        <label for="assign_seq">--assign-seq</label>
      </div>

      <div>
        <label for="threshold">Match Threshold:</label>
        <input id="threshold" v-model.number="form.threshold" type="number" step="0.05" min="0" max="1" />
      </div>

      <div>
        <button type="submit" :disabled="isRenaming || isLoadingDirs" class="btn-rename">
          <span v-if="isRenaming" class="loader"></span>
          <span v-else>Umbenennen</span>
        </button>
      </div>
    </form>

    <div v-if="log.length" class="log-container">
      <h3 v-if="false">Log</h3>
      <pre>{{ log.join('\n') }}</pre>
    </div>

    <div v-if="error" class="error-container">
      <strong>Fehler:</strong> {{ error }}
    </div>
  </div>
</template>

<script>
import debounce from "lodash.debounce";

export default {
  name: "App",
  data() {
    return {
      directories: [],
      form: {
        series: "",
        season: 1,
        directory: "",
        dry_run: true,
        assign_seq: false,
        threshold: 0.75,
        lang: "de",
      },
      log: [],
      error: "",
      isLoadingDirs: false,
      isRenaming: false,
    };
  },
  created() {
    this.debouncedFetch = debounce(this.fetchDirectories, 300);
  },
  mounted() {
    this.fetchDirectories(this.form.series, this.form.season);
  },
  watch: {
    "form.series"(newSeries) {
      this.debouncedFetch(newSeries, this.form.season);
    },
    "form.season"(newSeason) {
      this.debouncedFetch(this.form.series, newSeason);
    },
  },
  methods: {
    async fetchDirectories(series = "", season = null) {
      this.isLoadingDirs = true;
      this.error = "";

      const url = new URL("http://localhost:3333/directories");
      if (series) url.searchParams.set("series", series);
      if (season !== null && season !== "") {
        url.searchParams.set("season", season);
      }

      try {
        const res = await fetch(url);
        const data = await res.json();
        this.directories = data.directories;

        if (
          this.directories.length > 0 &&
          (!this.form.directory ||
            !this.directories.includes(this.form.directory))
        ) {
          this.form.directory = this.directories[0];
        }
      } catch {
        this.error = "Fehler beim Laden der Verzeichnisse";
      } finally {
        this.isLoadingDirs = false;
      }
    },

    async refreshDirectories() {
      this.isLoadingDirs = true;
      this.error = "";

      try {
        await fetch("http://localhost:3333/directories/refresh", {
          method: "POST",
        });
        await this.fetchDirectories(this.form.series, this.form.season);
      } catch {
        this.error = "Fehler beim Aktualisieren der Verzeichnisse";
      } finally {
        this.isLoadingDirs = false;
      }
    },

    async submitRename() {
      this.isRenaming = true;
      this.error = "";
      this.log = [];

      const formData = new FormData();
      Object.entries(this.form).forEach(([key, val]) =>
        formData.append(key, val)
      );

      try {
        const res = await fetch("http://localhost:3333/rename", {
          method: "POST",
          body: formData,
        });
        const data = await res.json();

        if (data.error) this.error = data.error;
        this.log = data.log || [];
        if (data.directories) this.directories = data.directories;
      } catch {
        this.error = "Fehler beim Umbenennen.";
      } finally {
        this.isRenaming = false;
      }
    },
  },
};
</script>