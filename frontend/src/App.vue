<template>
  <div class="layout-wrapper">
    <!-- Header -->
    <div class="header-section">
      <div class="header-content">
        <div class="header-main">
          <div class="header-text">
            <h1 class="header-title">
              🏗️ TECHNICAL DRAWING ANALYZER
            </h1>
            <p class="header-subtitle">
              Blueprint Analysis • Automated Cutting List Generation • Professional Cabinet Making
            </p>
          </div>
          <!-- <div class="header-time">
            <div class="time-label">Generated:</div>
            <div class="time-value">{{ currentDateTime }}</div>
          </div> -->
        </div>
      </div>
    </div>

    <div class="main-content">
      <!-- Upload Section -->
      <div class="section-card">
        <div class="section-header">
          <div class="section-header-content">
            <i class="pi pi-upload section-icon"></i>
            <span class="section-title">Upload Technical Drawing / Blueprint</span>
          </div>
        </div>

        <div class="info-message">
          <div class="info-icon">
            <i class="pi pi-list"></i>
          </div>
          <div class="info-content">
            <h4 class="info-title">📋 Supported Drawing Types:</h4>
            <ul class="info-list">
              <li>• Cabinet elevation drawings with dimensions</li>
              <li>• Technical blueprints with measurements</li>
              <li>• Construction drawings with section details</li>
              <li>• Hand-drawn or CAD-generated plans</li>
            </ul>
          </div>
        </div>

        <div class="upload-section">
          <div class="file-upload-container">
            <FileUpload
              mode="basic"
              name="file"
              accept="image/*"
              :maxFileSize="10000000"
              @select="handleFileSelect"
              :auto="false"
              chooseLabel="Choose Drawing File"
              class="custom-file-upload"
            />
            <div v-if="file" class="file-selected">
              📄 Selected: <strong>{{ file.name }}</strong>
            </div>
          </div>
          
          <Button
            @click="handleUpload"
            :disabled="!file || loading"
            :loading="loading"
            loadingIcon="pi pi-spin pi-search"
            class="analyze-button"
            size="large"
          >
            {{ loading ? '🔍 Analyzing Drawing...' : '🚀 Analyze & Generate Cutting List' }}
          </Button>
        </div>
      </div>

      <!-- Error Display -->
      <div v-if="error" class="error-message">
        <div class="error-icon">
          <i class="pi pi-exclamation-triangle"></i>
        </div>
        <div class="error-content">
          <h3 class="error-title">Error Processing Drawing</h3>
          <p class="error-text">{{ error }}</p>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-section">
        <div class="loading-content">
          <ProgressSpinner class="loading-spinner" />
          <h3 class="loading-title">🔍 Analyzing Technical Drawing</h3>
          <p class="loading-description">Extracting dimensions and analyzing cabinet structure...</p>
          <div class="loading-steps">
            <p>• Reading dimensional annotations</p>
            <p>• Identifying cabinet components</p>
            <p>• Generating optimized cutting list</p>
          </div>
        </div>
      </div>

      <!-- Results -->
      <div v-if="data" class="results-section">
        <!-- Analysis Summary -->
        <div class="section-card">
          <div class="section-header">
            <div class="section-header-main">
              <div class="section-header-content">
                <i class="pi pi-chart-bar section-icon"></i>
                <span class="section-title">DRAWING ANALYSIS SUMMARY</span>
              </div>
              <Button
                @click="showRawText = !showRawText"
                :label="showRawText ? '👁️ Hide Extracted Text' : '🔍 Show Extracted Text'"
                text
                size="small"
                class="toggle-button"
              />
            </div>
          </div>

          <div class="stats-grid">
            <div class="stat-card stat-green">
              <div class="stat-number">{{ totalPieces }}</div>
              <div class="stat-label">TOTAL COMPONENTS</div>
            </div>
            <div class="stat-card stat-blue">
              <div class="stat-number">{{ activeCategories }}</div>
              <div class="stat-label">COMPONENT TYPES</div>
            </div>
            <div class="stat-card stat-purple">
              <div class="stat-number">{{ totalMaterialArea }}</div>
              <div class="stat-label">TOTAL AREA (m²)</div>
            </div>
            <div class="stat-card stat-orange">
              <div class="stat-number">✓</div>
              <div class="stat-label">ANALYSIS COMPLETE</div>
            </div>
          </div>

          <div v-if="data.analysis_type" class="analysis-info">
            <strong>Analysis Type:</strong> {{ data.analysis_type.replace('_', ' ').toUpperCase() }}
          </div>
        </div>

        <!-- Raw Text Display -->
        <div v-if="showRawText && data.raw_text" class="section-card">
          <div class="section-header">
            <div class="section-header-content">
              <i class="pi pi-file-word section-icon"></i>
              <span class="section-title">Extracted Text Data</span>
            </div>
          </div>
          <div class="raw-text-container">
            <pre class="raw-text">{{ data.raw_text }}</pre>
          </div>
        </div>

        <!-- Generated Cutting List -->
        <div class="section-card">
          <div class="section-header">
            <div class="cutting-list-header">
              <h2 class="cutting-list-title">📋 GENERATED CUTTING LIST</h2>
              <p class="cutting-list-subtitle">Automatically generated from technical drawing analysis</p>
            </div>
          </div>

          <!-- Cutting List Sections -->
          <div v-if="data.categories && Object.keys(data.categories).length > 0">
            <div v-for="[categoryName, categoryData] in Object.entries(data.categories)" :key="categoryName">
              <CuttingListSection
                :categoryName="categoryName"
                :categoryData="categoryData"
              />
            </div>

            <!-- Grand Total -->
            <div class="grand-total-card">
              <div class="grand-total-content">
                <div class="grand-total-text">
                  <h3 class="grand-total-title">🎯 PROJECT TOTALS</h3>
                  <p class="grand-total-subtitle">Complete cutting list summary</p>
                </div>
                <div class="grand-total-stats">
                  <div class="grand-total-number">{{ totalPieces }}</div>
                  <div class="grand-total-label">TOTAL PIECES</div>
                  <div class="grand-total-area">{{ totalMaterialArea }} m²</div>
                  <div class="grand-total-area-label">MATERIAL AREA</div>
                </div>
              </div>
            </div>

            <!-- Export Options -->
            <div class="export-section">
              <div class="section-header">
                <div class="section-header-content">
                  <i class="pi pi-download section-icon"></i>
                  <span class="section-title">Export Options</span>
                </div>
              </div>
              <div class="export-buttons">
                <Button icon="pi pi-clipboard" label="Copy to Clipboard" size="small" class="export-button" />
                <Button icon="pi pi-file-excel" label="Export to Excel" severity="success" size="small" class="export-button" />
                <Button icon="pi pi-file-pdf" label="Export to PDF" severity="danger" size="small" class="export-button" />
                <Button icon="pi pi-print" label="Print Cutting List" severity="help" size="small" class="export-button" />
              </div>
            </div>
          </div>

          <div v-else class="no-components">
            <i class="pi pi-file-o no-components-icon"></i>
            <h3 class="no-components-title">No Components Found</h3>
            <p class="no-components-text">The drawing analysis did not identify any cabinet components. Please check that your image contains dimensional information.</p>
          </div>
        </div>

        <!-- Additional Information -->
        <div class="section-card">
          <div class="section-header">
            <div class="section-header-content">
              <i class="pi pi-info-circle section-icon"></i>
              <span class="section-title">Analysis Information</span>
            </div>
          </div>
          <div class="info-grid">
            <div class="info-card info-blue">
              <div class="info-card-icon">
                <i class="pi pi-cog"></i>
              </div>
              <div class="info-card-content">
                <h4 class="info-card-title">Processing Details</h4>
                <ul class="info-card-list">
                  <li>• Image processed using OCR technology</li>
                  <li>• Dimensions extracted and validated</li>
                  <li>• Components categorized by type</li>
                  <li>• Quantities calculated automatically</li>
                </ul>
              </div>
            </div>
            <div class="info-card info-warning">
              <div class="info-card-icon">
                <i class="pi pi-exclamation-triangle"></i>
              </div>
              <div class="info-card-content">
                <h4 class="info-card-title">⚠️ Important Notes</h4>
                <ul class="info-card-list">
                  <li>• Always verify dimensions manually</li>
                  <li>• Check material specifications</li>
                  <li>• Account for material wastage</li>
                  <li>• Consider grain direction requirements</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <footer class="footer-section">
      <div class="footer-content">
        <div class="footer-title">🏗️ Technical Drawing Analyzer</div>
        <p class="footer-description">
          Professional Cabinet Making Tool • Blueprint Analysis • Automated Cutting Lists
        </p>
        <div class="footer-note">
          Built for precision woodworking and cabinet making professionals
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Panel from 'primevue/panel'
import Button from 'primevue/button'
import FileUpload from 'primevue/fileupload'
import Message from 'primevue/message'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Badge from 'primevue/badge'
import ProgressSpinner from 'primevue/progressspinner'
import CuttingListSection from './components/CuttingListSection.vue'
// import ConsolidatedCuttingList from './components/ConsolidatedCuttingList.vue'


// const viewMode = ref('consolidated') // Default to consolidated view

// Reactive data
const file = ref(null)
const data = ref(null)
const loading = ref(false)
const error = ref(null)
const showRawText = ref(false)
const currentDateTime = ref('')

// Computed properties
const totalPieces = computed(() => {
  if (!data.value?.categories) return 0
  return Object.values(data.value.categories).reduce((total, category) => 
    total + category.total_pieces, 0
  )
})

const activeCategories = computed(() => {
  if (!data.value?.categories) return 0
  return Object.values(data.value.categories).filter(category => 
    category.items.length > 0
  ).length
})

const totalMaterialArea = computed(() => {
  if (!data.value?.categories) return '0.00'
  let totalArea = 0
  Object.values(data.value.categories).forEach(category => {
    category.items.forEach(item => {
      totalArea += (item.width * item.height * item.quantity) / 1000000 // Convert to m²
    })
  })
  return totalArea.toFixed(2)
})

// Methods
const updateCurrentDateTime = () => {
  currentDateTime.value = new Date().toLocaleString('en-GB', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleFileSelect = (event) => {
  file.value = event.files[0]
  data.value = null
  error.value = null
}

const handleUpload = async () => {
  if (!file.value) return
  
  loading.value = true
  error.value = null
  
  const formData = new FormData()
  formData.append('file', file.value)

  try {
    const healthResponse = await fetch('http://localhost:5000/health')
    if (!healthResponse.ok) {
      throw new Error('Backend server is not running on http://localhost:5000')
    }

    const response = await fetch('http://localhost:5000/upload', {
      method: 'POST',
      body: formData,
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || `Server error: ${response.status}`)
    }
    
    const result = await response.json()
    
    if (result.status === 'success') {
      data.value = result
    } else {
      error.value = result.error || 'Unknown error occurred'
    }
  } catch (err) {
    console.error('Upload error:', err)
    if (err.message.includes('fetch')) {
      error.value = 'Cannot connect to backend server. Make sure Flask is running on http://localhost:5000'
    } else {
      error.value = 'Error uploading file: ' + err.message
    }
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  updateCurrentDateTime()
  // Update time every minute
  setInterval(updateCurrentDateTime, 60000)
})
</script>

<style scoped>
/* Reset and base styles */
* {
  box-sizing: border-box;
}

.layout-wrapper {
  min-height: 100vh;
  background-color: #f8fafc;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #1e293b;
  width: 100%;
}

/* Header styles */
.header-section {
  background: linear-gradient(135deg, #1e293b, #334155);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  width: 100%;
}

.header-content {
  padding: 2rem 3rem;
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 2rem;
}

.header-text {
  text-align: left;
}

.header-title {
  font-size: 2.25rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  color: #ffffff;
}

.header-subtitle {
  font-size: 1.125rem;
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
}

.header-time {
  text-align: right;
}

.time-label {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 0.25rem;
}

.time-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #ffffff;
}

/* Main content */
.main-content {
  padding: 2rem 3rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* Section card styles */
.section-card {
  background: linear-gradient(135deg, #ffffff, #f8fafc);
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  margin-bottom: 2rem;
  overflow: hidden;
}

.section-header {
  padding: 2rem;
  background: linear-gradient(135deg, #f8fafc, #e2e8f0);
  border-bottom: 1px solid #e2e8f0;
}

.section-header-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.section-header-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.section-icon {
  font-size: 1.5rem;
  color: #3b82f6;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
}

/* Info message styles */
.info-message {
  background: linear-gradient(135deg, #dbeafe, #bfdbfe);
  border: 1px solid #93c5fd;
  border-radius: 12px;
  padding: 1.5rem;
  margin: 2rem;
  display: flex;
  gap: 1rem;
}

.info-icon {
  color: #1d4ed8;
  font-size: 1.25rem;
  flex-shrink: 0;
  padding-top: 0.25rem;
}

.info-content {
  flex: 1;
}

.info-title {
  font-weight: 700;
  margin: 0 0 0.75rem 0;
  color: #1e293b;
}

.info-list {
  margin: 0;
  padding-left: 1rem;
  color: #374151;
  font-size: 0.875rem;
}

.info-list li {
  margin-bottom: 0.25rem;
}

/* Upload section styles */
.upload-section {
  display: flex;
  gap: 1.5rem;
  align-items: flex-end;
  padding: 2rem;
  flex-wrap: wrap;
}

.file-upload-container {
  flex: 1;
  min-width: 250px;
}

.file-selected {
  margin-top: 0.5rem;
  color: #16a34a;
  font-size: 0.875rem;
}

.analyze-button {
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border: none;
  color: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 200px;
}

.analyze-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3);
}

/* Error message styles */
.error-message {
  background: linear-gradient(135deg, #fee2e2, #fecaca);
  border: 1px solid #fca5a5;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  display: flex;
  gap: 1rem;
}

.error-icon {
  color: #dc2626;
  font-size: 1.25rem;
  flex-shrink: 0;
  padding-top: 0.25rem;
}

.error-content {
  flex: 1;
}

.error-title {
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  color: #dc2626;
}

.error-text {
  margin: 0;
  color: #7f1d1d;
  font-size: 0.875rem;
}

/* Loading section styles */
.loading-section {
  background: linear-gradient(135deg, #ffffff, #f8fafc);
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  margin-bottom: 2rem;
}

.loading-content {
  text-align: center;
  padding: 3rem 2rem;
}

.loading-spinner {
  margin-bottom: 1.5rem;
}

.loading-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #3b82f6;
  margin: 0 0 0.75rem 0;
}

.loading-description {
  color: #64748b;
  margin: 0 0 1.5rem 0;
  font-size: 1rem;
}

.loading-steps {
  color: #64748b;
  font-size: 0.875rem;
}

.loading-steps p {
  margin: 0.25rem 0;
}

/* Stats grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  padding: 2rem;
}

.stat-card {
  text-align: center;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  color: white;
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-green {
  background: linear-gradient(135deg, #10b981, #059669);
}

.stat-blue {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.stat-purple {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
}

.stat-orange {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.75rem;
  font-weight: 500;
  opacity: 0.9;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Analysis info */
.analysis-info {
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #dbeafe, #bfdbfe);
  border: 1px solid #93c5fd;
  border-radius: 8px;
  margin: 0 2rem 2rem 2rem;
  color: #1e40af;
}

/* Raw text container */
.raw-text-container {
  padding: 2rem;
}

.raw-text {
  background-color: #f1f5f9;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  font-family: 'Courier New', Consolas, Monaco, monospace;
  font-size: 0.875rem;
  line-height: 1.4;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 400px;
  overflow-y: auto;
  margin: 0;
}

/* Cutting list header */
.cutting-list-header {
  padding: 2rem;
}

.cutting-list-title {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  color: #1e293b;
}

.cutting-list-subtitle {
  color: #64748b;
  margin: 0;
  font-size: 1rem;
}

/* Grand total card */
.grand-total-card {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border-radius: 12px;
  margin: 2rem;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.grand-total-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem;
  flex-wrap: wrap;
  gap: 2rem;
}

.grand-total-text {
  text-align: left;
}

.grand-total-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}

.grand-total-subtitle {
  opacity: 0.8;
  margin: 0;
  font-size: 0.875rem;
}

.grand-total-stats {
  text-align: right;
}

.grand-total-number {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.grand-total-label {
  font-size: 0.75rem;
  opacity: 0.8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.grand-total-area {
  font-size: 1.25rem;
  font-weight: 600;
  margin-top: 0.75rem;
}

.grand-total-area-label {
  font-size: 0.625rem;
  opacity: 0.8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Export section */
.export-section {
  background: linear-gradient(135deg, #ffffff, #f8fafc);
  border-top: 1px solid #e2e8f0;
}

.export-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding: 0 2rem 2rem 2rem;
}

.export-button {
  font-size: 0.875rem;
  padding: 0.75rem 1.25rem;
}

/* No components */
.no-components {
  text-align: center;
  color: #64748b;
  padding: 3rem 2rem;
}

.no-components-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  display: block;
}

.no-components-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0 0 0.75rem 0;
  color: #1e293b;
}

.no-components-text {
  margin: 0;
  font-size: 0.875rem;
}

/* Info grid */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  padding: 2rem;
}

.info-card {
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  gap: 1rem;
}

.info-blue {
  background: linear-gradient(135deg, #dbeafe, #bfdbfe);
  border: 1px solid #93c5fd;
}

.info-warning {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  border: 1px solid #fbbf24;
}

.info-card-icon {
  flex-shrink: 0;
  padding-top: 0.25rem;
}

.info-blue .info-card-icon {
  color: #1d4ed8;
}

.info-warning .info-card-icon {
  color: #d97706;
}

.info-card-content {
  flex: 1;
}

.info-card-title {
  font-weight: 700;
  margin: 0 0 0.75rem 0;
  color: #1e293b;
  font-size: 1rem;
}

.info-card-list {
  margin: 0;
  padding-left: 1rem;
  color: #374151;
  font-size: 0.875rem;
}

.info-card-list li {
  margin-bottom: 0.25rem;
}

/* Footer */
.footer-section {
  background: linear-gradient(135deg, #1e293b, #334155);
  color: white;
  padding: 3rem;
  margin-top: 4rem;
}

.footer-content {
  text-align: center;
}

.footer-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.footer-description {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.875rem;
  margin: 0 0 1rem 0;
}

.footer-note {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
}

/* Toggle button */
.toggle-button {
  font-size: 0.875rem;
  color: #3b82f6;
}

/* Responsive design */
@media (max-width: 1024px) {
  .main-content {
    padding: 1.5rem 2rem;
  }
  
  .header-content {
    padding: 1.5rem 2rem;
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
  
  .stat-number {
    font-size: 2rem;
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: 1rem;
  }
  
  .header-content {
    padding: 1rem;
  }
  
  .header-main {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .header-text {
    text-align: center;
  }
  
  .header-time {
    text-align: center;
  }
  
  .header-title {
    font-size: 1.75rem;
  }
  
  .header-subtitle {
    font-size: 1rem;
  }
  
  .section-header {
    padding: 1.5rem;
  }
  
  .section-title {
    font-size: 1.25rem;
  }
  
  .upload-section {
    flex-direction: column;
    padding: 1.5rem;
    align-items: stretch;
  }
  
  .analyze-button {
    min-width: auto;
    width: 100%;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    padding: 1.5rem;
  }
  
  .grand-total-content {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .grand-total-stats {
    text-align: center;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
    padding: 1.5rem;
  }
  
  .export-buttons {
    flex-direction: column;
    padding: 0 1.5rem 1.5rem 1.5rem;
  }
  
  .export-button {
    width: 100%;
    justify-content: center;
  }
  
  .cutting-list-header {
    padding: 1.5rem;
  }
  
  .cutting-list-title {
    font-size: 1.5rem;
  }
  
  .section-header-main {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }
  
  .toggle-button {
    align-self: flex-start;
  }
}

@media (max-width: 480px) {
  .header-title {
    font-size: 1.5rem;
  }
  
  .header-subtitle {
    font-size: 0.875rem;
  }
  
  .stat-number {
    font-size: 1.75rem;
  }
  
  .grand-total-number {
    font-size: 2rem;
  }
  
  .footer-content {
    padding: 1rem;
  }
}
</style>