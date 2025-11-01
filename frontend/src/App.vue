<template>
  <div id="app" class="app">
    <h1>Media Renamer</h1>

    <div class="renamer-grid">
      <!-- Episode Renamer -->
      <div class="renamer-section">
        <h2>📺 Episode Renamer</h2>
        <form @submit.prevent="submitEpisodeRename" class="form-container">
          <div>
            <label for="ep-series">Serie:</label>
            <input
              id="ep-series"
              v-model="episodeForm.series"
              type="text"
              placeholder="Name der Serie"
              required
            />
          </div>

          <div>
            <label for="ep-season">Staffel:</label>
            <input
              id="ep-season"
              v-model.number="episodeForm.season"
              type="number"
              min="1"
              required
            />
          </div>

          <div>
            <label for="ep-directory">Verzeichnis:</label>
            <select
              id="ep-directory"
              v-model="episodeForm.directory"
              :disabled="isLoadingEpisodeDirs || isRenamingEpisodes"
              required
            >
              <option v-for="dir in episodeDirectories" :key="dir" :value="dir">
                {{ dir }}
              </option>
            </select>

            <button
              type="button"
              @click="refreshEpisodeDirectories"
              :disabled="isLoadingEpisodeDirs || isRenamingEpisodes"
              class="btn-refresh"
            >
              <span v-if="isLoadingEpisodeDirs" class="loader-sm"></span>
              <span v-else>Verzeichnisse neu laden</span>
            </button>
          </div>

          <div>
            <label for="ep-lang">Sprache:</label>
            <select id="ep-lang" v-model="episodeForm.lang">
              <option value="de">Deutsch</option>
              <option value="en">Englisch</option>
            </select>
          </div>

          <div class="checkbox-group">
            <input id="ep-dry_run" v-model="episodeForm.dry_run" type="checkbox" />
            <label for="ep-dry_run">--dry-run</label>
          </div>
          <div class="checkbox-group">
            <input id="ep-assign_seq" v-model="episodeForm.assign_seq" type="checkbox" />
            <label for="ep-assign_seq">--assign-seq</label>
          </div>

          <div>
            <label for="ep-threshold">Match Threshold:</label>
            <input
              id="ep-threshold"
              v-model.number="episodeForm.threshold"
              type="number"
              step="0.05"
              min="0"
              max="1"
            />
          </div>

          <div>
            <button
              type="submit"
              :disabled="isRenamingEpisodes || isLoadingEpisodeDirs"
              class="btn-rename"
            >
              <span v-if="isRenamingEpisodes" class="loader"></span>
              <span v-else>Umbenennen</span>
            </button>
          </div>
        </form>
      </div>

      <!-- Music Renamer -->
      <div class="renamer-section">
        <h2>🎵 Music Renamer</h2>
        <form @submit.prevent="submitMusicRename" class="form-container">
          <div>
            <label for="music-artist">Künstler:</label>
            <input
              id="music-artist"
              v-model="musicForm.artist"
              type="text"
              placeholder="Name des Künstlers"
              required
            />
          </div>

          <div>
            <label for="music-album">Album (optional):</label>
            <input
              id="music-album"
              v-model="musicForm.album"
              type="text"
              placeholder="Album zum Filtern"
            />
          </div>

          <div>
            <label for="music-directory">Verzeichnis:</label>
            <select
              id="music-directory"
              v-model="musicForm.directory"
              :disabled="isLoadingMusicDirs || isRenamingMusic"
              required
            >
              <option v-if="!musicDirectories.length" disabled value="">
                Keine Verzeichnisse gefunden
              </option>
              <option v-for="dir in musicDirectories" :key="dir" :value="dir">
                {{ dir }}
              </option>
            </select>

            <button
              type="button"
              @click="refreshMusicDirectories"
              :disabled="isLoadingMusicDirs || isRenamingMusic"
              class="btn-refresh"
            >
              <span v-if="isLoadingMusicDirs" class="loader-sm"></span>
              <span v-else>Verzeichnisse neu laden</span>
            </button>
          </div>

          <div class="checkbox-group">
            <input id="music-dry_run" v-model="musicForm.dry_run" type="checkbox" />
            <label for="music-dry_run">--dry-run</label>
          </div>

          <div class="spacer"></div>
          <div class="spacer"></div>
          <div class="spacer"></div>

          <div>
            <button
              type="submit"
              :disabled="isRenamingMusic || isLoadingMusicDirs"
              class="btn-rename"
            >
              <span v-if="isRenamingMusic" class="loader"></span>
              <span v-else>Umbenennen</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Shared Log Container -->
    <div class="log-container">
      <h3>📋 Log-Ausgabe</h3>
      <pre v-if="log.length">{{ log.join("\n") }}</pre>
      <p v-else class="log-placeholder">Keine Einträge</p>
    </div>

    <div v-if="error" class="error-container">
      <strong>❌ Fehler:</strong> {{ error }}
    </div>
  </div>
</template>

<script>
import debounce from "lodash.debounce";

export default {
  name: "App",
  data() {
    return {
      // Episode Renamer
      episodeDirectories: [],
      episodeForm: {
        series: "",
        season: 1,
        directory: "",
        dry_run: true,
        assign_seq: false,
        threshold: 0.75,
        lang: "de",
      },
      isLoadingEpisodeDirs: false,
      isRenamingEpisodes: false,

      // Music Renamer
      musicDirectories: [],
      musicForm: {
        artist: "",
        album: "",
        directory: "",
        dry_run: true,
      },
      isLoadingMusicDirs: false,
      isRenamingMusic: false,

      // Shared
      log: [],
      error: "",
      API_BASE: import.meta.env.VITE_API_BASE_URL || "/api",
    };
  },
  created() {
    this.debouncedFetchEpisodes = debounce(this.fetchEpisodeDirectories, 300);
    this.debouncedFetchMusic = debounce(this.fetchMusicDirectories, 300);
  },
  mounted() {
    this.fetchEpisodeDirectories(this.episodeForm.series, this.episodeForm.season);
    this.fetchMusicDirectories(this.musicForm.artist, this.musicForm.album);
  },
  watch: {
    "episodeForm.series"(newSeries) {
      this.debouncedFetchEpisodes(newSeries, this.episodeForm.season);
    },
    "episodeForm.season"(newSeason) {
      this.debouncedFetchEpisodes(this.episodeForm.series, newSeason);
    },
    "musicForm.artist"(newArtist) {
      this.debouncedFetchMusic(newArtist, this.musicForm.album);
    },
    "musicForm.album"(newAlbum) {
      this.debouncedFetchMusic(this.musicForm.artist, newAlbum);
    },
  },
  methods: {
    // === Episode Renamer Methods ===
    async fetchEpisodeDirectories(series = "", season = null) {
      this.isLoadingEpisodeDirs = true;
      this.error = "";

      const url = new URL(`${this.API_BASE}/directories`, window.location.origin);
      if (series) url.searchParams.set("series", series);
      if (season !== null && season !== "") {
        url.searchParams.set("season", season);
      }

      try {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        this.episodeDirectories = data.directories;
        if (
          this.episodeDirectories.length > 0 &&
          (!this.episodeForm.directory ||
            !this.episodeDirectories.includes(this.episodeForm.directory))
        ) {
          this.episodeForm.directory = this.episodeDirectories[0];
        }
      } catch (err) {
        this.error = `Fehler beim Laden der Episode-Verzeichnisse: ${err.message}`;
      } finally {
        this.isLoadingEpisodeDirs = false;
      }
    },

    async refreshEpisodeDirectories() {
      this.isLoadingEpisodeDirs = true;
      this.error = "";

      try {
        const res = await fetch(`${this.API_BASE}/directories/refresh`, {
          method: "POST",
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        await this.fetchEpisodeDirectories(this.episodeForm.series, this.episodeForm.season);
      } catch (err) {
        this.error = `Fehler beim Aktualisieren der Episode-Verzeichnisse: ${err.message}`;
      } finally {
        this.isLoadingEpisodeDirs = false;
      }
    },

    async submitEpisodeRename() {
      this.isRenamingEpisodes = true;
      this.error = "";
      this.log = [];

      const formData = new FormData();
      Object.entries(this.episodeForm).forEach(([key, val]) =>
        formData.append(key, val)
      );

      try {
        const res = await fetch(`${this.API_BASE}/rename`, {
          method: "POST",
          body: formData,
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        if (data.error) this.error = data.error;
        this.log = data.log || [];
        if (data.directories) this.episodeDirectories = data.directories;
      } catch (err) {
        this.error = `Fehler beim Umbenennen der Episoden: ${err.message}`;
      } finally {
        this.isRenamingEpisodes = false;
      }
    },

    // === Music Renamer Methods ===
    async fetchMusicDirectories(artist = "", album = "") {
      this.isLoadingMusicDirs = true;
      this.error = "";

      const url = new URL(`${this.API_BASE}/music/directories`, window.location.origin);
      if (artist) url.searchParams.set("artist", artist);
      if (album) url.searchParams.set("album", album);

      try {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        this.musicDirectories = data.directories;
        if (
          this.musicDirectories.length > 0 &&
          (!this.musicForm.directory ||
            !this.musicDirectories.includes(this.musicForm.directory))
        ) {
          this.musicForm.directory = this.musicDirectories[0];
        } else if (this.musicDirectories.length === 0) {
          this.musicForm.directory = "";
        }
      } catch (err) {
        this.error = `Fehler beim Laden der Musik-Verzeichnisse: ${err.message}`;
      } finally {
        this.isLoadingMusicDirs = false;
      }
    },

    async refreshMusicDirectories() {
      this.isLoadingMusicDirs = true;
      this.error = "";

      try {
        const res = await fetch(`${this.API_BASE}/music/directories/refresh`, {
          method: "POST",
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        await this.fetchMusicDirectories(this.musicForm.artist, this.musicForm.album);
      } catch (err) {
        this.error = `Fehler beim Aktualisieren der Musik-Verzeichnisse: ${err.message}`;
      } finally {
        this.isLoadingMusicDirs = false;
      }
    },

    async submitMusicRename() {
      this.isRenamingMusic = true;
      this.error = "";
      this.log = [];

      const formData = new FormData();
      formData.append("artist", this.musicForm.artist);
      formData.append("directory", this.musicForm.directory);
      formData.append("dry_run", this.musicForm.dry_run);

      try {
        const res = await fetch(`${this.API_BASE}/music/rename`, {
          method: "POST",
          body: formData,
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        if (data.error) this.error = data.error;
        this.log = data.log || [];
        if (data.directories) this.musicDirectories = data.directories;
      } catch (err) {
        this.error = `Fehler beim Umbenennen der Musik-Dateien: ${err.message}`;
      } finally {
        this.isRenamingMusic = false;
      }
    },
  },
};
</script>

<style scoped>
.app {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
}

.renamer-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

@media (max-width: 900px) {
  .renamer-grid {
    grid-template-columns: 1fr;
  }
}

.renamer-section {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #ddd;
}

.renamer-section h2 {
  margin-top: 0;
  font-size: 1.3em;
  border-bottom: 2px solid #333;
  padding-bottom: 10px;
  margin-bottom: 15px;
}

.form-container {
  background: #1e1e1e;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-container > div {
  display: flex;
  flex-direction: column;
}

label {
  font-weight: bold;
  margin-bottom: 5px;
  color: #fff;
}

input[type="text"],
input[type="number"],
select {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

.checkbox-group {
  flex-direction: row !important;
  align-items: center;
  gap: 8px;
  margin-top: 0;
}

.checkbox-group input[type="checkbox"] {
  width: auto;
  margin: 0;
  padding: 0;
  flex: 0 0 auto;
}

.checkbox-group label {
  margin: 0;
  font-weight: normal;
  color: #fff;
  white-space: nowrap;
  hyphens: none;
}

.btn-refresh,
.btn-rename {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 15px;
  min-height: 40px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-top: 10px;
}

.btn-refresh:hover:not(:disabled),
.btn-rename:hover:not(:disabled) {
  background: #0056b3;
}

.btn-refresh:disabled,
.btn-rename:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.spacer {
  height: 0;
}

.log-container {
  border: 1px solid #333;
  border-radius: 8px;
  padding: 15px;
  background: #f4f4f4;
  margin-bottom: 20px;
  min-height: 200px;
}

.log-container h3 {
  margin-top: 0;
  font-size: 1.2em;
  margin-bottom: 10px;
}

.log-container pre {
  background: #fff;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 13px;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  margin: 0;
}

.log-placeholder {
  color: #888;
  font-style: italic;
  margin: 0;
}

.error-container {
  background: #ffebee;
  border: 1px solid #f44336;
  border-radius: 4px;
  padding: 15px;
  color: #c62828;
  margin-bottom: 20px;
}

.loader,
.loader-sm {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border: 3px solid #f3f3f3;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.loader {
  width: 20px;
  height: 20px;
}

.loader-sm {
  width: 16px;
  height: 16px;
}

@keyframes spin {
  to {
    transform: translate(-50%, -50%) rotate(360deg);
  }
}
</style>
