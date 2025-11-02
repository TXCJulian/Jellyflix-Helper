<template>
  <div id="app" class="app">
    <h1>Media Renamer</h1>

    <div class="pane-grid">
      <!-- Episodes Pane -->
      <div class="pane">
        <h2>Episode Renamer</h2>
        <form @submit.prevent="submitRenameEpisodes" class="form-container">
          <div>
            <label class="label_top" for="series">Serie:</label>
            <input id="series" v-model="ep.form.series" type="text" placeholder="Name der Serie" required />
          </div>

          <div>
            <label for="season">Staffel:</label>
            <input id="season" v-model.number="ep.form.season" type="number" min="1" required />
          </div>

          <div>
            <label for="directory-ep">Verzeichnis:</label>
            <select id="directory-ep" v-model="ep.form.directory" :disabled="ep.isLoadingDirs || ep.isRenaming"
              required>
              <template v-if="ep.directories.length > 0">
                <option v-for="dir in ep.directories" :key="dir" :value="dir">
                  {{ dir }}
                </option>
              </template>
              <option v-else disabled value="">Keine Ordner gefunden</option>
            </select>

            <button type="button" @click="refreshEpisodeDirectories" :disabled="ep.isLoadingDirs || ep.isRenaming"
              class="btn-refresh">
              <span v-if="ep.isLoadingDirs" class="loader-sm"></span>
              <span v-else>Verzeichnisse neu laden</span>
            </button>
          </div>

          <div>
            <label for="lang">Sprache:</label>
            <select id="lang" v-model="ep.form.lang">
              <option value="de">Deutsch</option>
              <option value="en">Englisch</option>
            </select>
          </div>

          <div class="checkbox-group">
            <input id="dry_run_ep" v-model="ep.form.dry_run" type="checkbox" />
            <label for="dry_run_ep">--dry-run</label>
          </div>

          <div class="checkbox-group">
            <input id="assign_seq" v-model="ep.form.assign_seq" type="checkbox" />
            <label for="assign_seq">--assign-seq</label>
          </div>

          <div>
            <label for="threshold">Match Threshold:</label>
            <input id="threshold" v-model.number="ep.form.threshold" type="number" step="0.05" min="0" max="1" />
          </div>

          <div>
            <button type="submit" :disabled="ep.isRenaming || ep.isLoadingDirs" class="btn-rename">
              <span v-if="ep.isRenaming" class="loader"></span>
              <span v-else>Umbenennen</span>
            </button>
          </div>
        </form>

        <div v-if="ep.error" class="error-container">
          <strong>Fehler:</strong> {{ ep.error }}
        </div>
      </div>

      <!-- Music Pane -->
      <div class="pane">
        <h2>Music Renamer</h2>
        <form @submit.prevent="submitRenameMusic" class="form-container">
          <div>
            <label class="label_top" for="artist">Künstler:</label>
            <input id="artist" v-model="mu.form.artist" type="text" placeholder="Name des Künstlers"/>
          </div>

          <div>
            <label for="album">Album:</label>
            <input id="album" v-model="mu.form.album" type="text" placeholder="Name des Albums" />
          </div>

          <div>
            <label for="directory-mu">Verzeichnis:</label>
            <select id="directory-mu" v-model="mu.form.directory" :disabled="mu.isLoadingDirs || mu.isRenaming"
              required>
              <template v-if="mu.directories.length > 0">
                <option v-for="dir in mu.directories" :key="dir" :value="dir">
                  {{ dir }}
                </option>
              </template>
              <option v-else disabled value="">Keine Ordner gefunden</option>
            </select>

            <button type="button" @click="refreshMusicDirectories" :disabled="mu.isLoadingDirs || mu.isRenaming"
              class="btn-refresh">
              <span v-if="mu.isLoadingDirs" class="loader-sm"></span>
              <span v-else>Verzeichnisse neu laden</span>
            </button>
          </div>

          <div class="checkbox-group">
            <input id="dry_run_mu" v-model="mu.form.dry_run" type="checkbox" />
            <label for="dry_run_mu">--dry-run</label>
          </div>

          <div>
            <button type="submit" :disabled="mu.isRenaming || mu.isLoadingDirs" class="btn-rename">
              <span v-if="mu.isRenaming" class="loader"></span>
              <span v-else>Umbenennen</span>
            </button>
          </div>
        </form>

        <div v-if="mu.error" class="error-container">
          <strong>Fehler:</strong> {{ mu.error }}
        </div>
      </div>

      <!-- Log Section - spans full width -->
      <div class="log-section">
        <div class="log-container">
          <pre>{{ combinedLog }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import debounce from "lodash.debounce";

export default {
  name: "App",
  data() {
    return {
      // Episodes state
      ep: {
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
      },
      // Music state
      mu: {
        directories: [],
        form: {
          artist: "",
          album: "",
          directory: "",
          dry_run: true,
        },
        log: [],
        error: "",
        isLoadingDirs: false,
        isRenaming: false,
      },
      hasStartedRename: false,
  // Base URL: falls VITE_API_BASE_URL leer/undefiniert ist, Same-Origin verwenden
  API_BASE: (import.meta.env.VITE_API_BASE_URL && import.meta.env.VITE_API_BASE_URL.trim()) || window.location.origin,
    };
  },
  computed: {
    combinedLog() {
      const logs = [];
      if (this.ep.log.length > 0) {
        logs.push(...this.ep.log);
      }
      if (this.mu.log.length > 0) {
        if (logs.length > 0) logs.push(''); // Empty line separator
        logs.push(...this.mu.log);
      }
      return logs.length > 0 ? logs.join('\n') : (this.hasStartedRename ? '' : 'Bereit für Umbenennung...');
    }
  },
  created() {
    this.debouncedFetchEpisodes = debounce(this.fetchEpisodeDirectories, 300);
    this.debouncedFetchMusic = debounce(this.fetchMusicDirectories, 300);
  },
  mounted() {
    this.fetchEpisodeDirectories();
    this.fetchMusicDirectories();
  },
  watch: {
    // Episodes filters
    "ep.form.series"() { this.debouncedFetchEpisodes(); },
    "ep.form.season"() { this.debouncedFetchEpisodes(); },
    // Music filters
    "mu.form.artist"() { this.debouncedFetchMusic(); },
    "mu.form.album"() { this.debouncedFetchMusic(); },
  },
  methods: {
    // Episodes: directories
    async fetchEpisodeDirectories() {
      this.ep.isLoadingDirs = true;
      this.ep.error = "";

      const url = new URL('/directories/tvshows', this.API_BASE);
      if (this.ep.form.series) url.searchParams.set("series", this.ep.form.series);
      if (this.ep.form.season !== null && this.ep.form.season !== "") {
        url.searchParams.set("season", this.ep.form.season);
      }

      try {
        const res = await fetch(url);
        const data = await res.json();
        this.ep.directories = data.directories || [];
        if (this.ep.directories.length > 0) {
          if (!this.ep.form.directory || !this.ep.directories.includes(this.ep.form.directory)) {
            this.ep.form.directory = this.ep.directories[0];
          }
        } else {
          this.ep.form.directory = "";
        }
      } catch {
        this.ep.error = "Fehler beim Laden der Verzeichnisse";
      } finally {
        this.ep.isLoadingDirs = false;
      }
    },
    async refreshEpisodeDirectories() {
      this.ep.isLoadingDirs = true;
      this.ep.error = "";
      try {
        const url = new URL('/directories/refresh', this.API_BASE);
        await fetch(url, { method: "POST" });
      } catch {
        // ignore
      }
      await this.fetchEpisodeDirectories();
      this.ep.isLoadingDirs = false;
    },

    // Music: directories
    async fetchMusicDirectories() {
      this.mu.isLoadingDirs = true;
      this.mu.error = "";

      const url = new URL('/directories/music', this.API_BASE);
      if (this.mu.form.artist) url.searchParams.set("artist", this.mu.form.artist);
      if (this.mu.form.album) url.searchParams.set("album", this.mu.form.album);

      try {
        const res = await fetch(url);
        const data = await res.json();
        this.mu.directories = data.directories || [];
        if (this.mu.directories.length > 0) {
          if (!this.mu.form.directory || !this.mu.directories.includes(this.mu.form.directory)) {
            this.mu.form.directory = this.mu.directories[0];
          }
        } else {
          this.mu.form.directory = "";
        }
      } catch {
        this.mu.error = "Fehler beim Laden der Verzeichnisse";
      } finally {
        this.mu.isLoadingDirs = false;
      }
    },
    async refreshMusicDirectories() {
      this.mu.isLoadingDirs = true;
      this.mu.error = "";
      try {
        const url = new URL('/directories/refresh', this.API_BASE);
        await fetch(url, { method: "POST" });
      } catch {
        // ignore
      }
      await this.fetchMusicDirectories();
      this.mu.isLoadingDirs = false;
    },

    // Episodes: submit
    async submitRenameEpisodes() {
      this.hasStartedRename = true;
      this.ep.isRenaming = true;
      this.ep.error = "";
      this.ep.log = [];
      this.mu.log = []; // Clear music logs as well

      const formData = new FormData();
      formData.append("series", this.ep.form.series);
      formData.append("season", this.ep.form.season);
      formData.append("directory", this.ep.form.directory);
      formData.append("dry_run", this.ep.form.dry_run);
      formData.append("assign_seq", this.ep.form.assign_seq);
      formData.append("threshold", this.ep.form.threshold);
      formData.append("lang", this.ep.form.lang);

      try {
        const url = new URL('/rename/episodes', this.API_BASE);
        const res = await fetch(url, {
          method: "POST",
          body: formData,
        });
        const data = await res.json();
        if (data.error) this.ep.error = data.error;
        this.ep.log = data.log || [];
        if (data.directories) this.ep.directories = data.directories;
      } catch {
        this.ep.error = "Fehler beim Umbenennen.";
      } finally {
        this.ep.isRenaming = false;
      }
    },

    // Music: submit
    async submitRenameMusic() {
      this.hasStartedRename = true;
      this.mu.isRenaming = true;
      this.mu.error = "";
      this.mu.log = [];
      this.ep.log = []; // Clear episode logs as well

      const formData = new FormData();
      formData.append("directory", this.mu.form.directory);
      formData.append("dry_run", this.mu.form.dry_run);

      try {
        const url = new URL('/rename/music', this.API_BASE);
        const res = await fetch(url, {
          method: "POST",
          body: formData,
        });
        const data = await res.json();
        if (data.error) this.mu.error = data.error;
        this.mu.log = data.log || [];
        if (data.directories) this.mu.directories = data.directories;
      } catch {
        this.mu.error = "Fehler beim Umbenennen.";
      } finally {
        this.mu.isRenaming = false;
      }
    },
  },
};
</script>
