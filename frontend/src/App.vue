<template>
  <div class="min-h-screen surface-ground">
    <!-- Header -->
    <div class="bg-primary text-primary-color shadow-8">
      <div class="container mx-auto px-6 py-6">
        <div class="flex align-items-center justify-content-between">
          <div>
            <h1 class="text-4xl font-bold mb-2 m-0">
              🏗️ TECHNICAL DRAWING ANALYZER
            </h1>
            <p class="text-primary-100 text-lg m-0">
              Blueprint Analysis • Automated Cutting List Generation • Professional Cabinet Making
            </p>
          </div>
          <!-- <div class="text-right">
            <div class="text-sm text-primary-100">Generated:</div>
            <div class="text-xl font-bold">{{ currentDateTime }}</div>
          </div> -->
        </div>
      </div>
    </div>

    <div class="container mx-auto px-6 py-8">
      <!-- Upload Section -->
      <Panel class="mb-8">
        <template #header>
          <div class="flex align-items-center gap-3">
            <i class="pi pi-upload text-2xl"></i>
            <span class="text-2xl font-bold">Upload Technical Drawing / Blueprint</span>
          </div>
        </template>

        <Message 
          severity="info" 
          :closable="false" 
          class="mb-6"
        >
          <template #messageicon>
            <i class="pi pi-list"></i>
          </template>
          <div>
            <h4 class="font-bold mb-2 mt-0">📋 Supported Drawing Types:</h4>
            <ul class="text-sm m-0 pl-4">
              <li>• Cabinet elevation drawings with dimensions</li>
              <li>• Technical blueprints with measurements</li>
              <li>• Construction drawings with section details</li>
              <li>• Hand-drawn or CAD-generated plans</li>
            </ul>
          </div>
        </Message>

        <div class="flex flex-column lg:flex-row gap-6 align-items-start">
          <div class="flex-1">
            <FileUpload
              mode="basic"
              name="file"
              accept="image/*"
              :maxFileSize="10000000"
              @select="handleFileSelect"
              :auto="false"
              chooseLabel="Choose Drawing File"
              class="w-full"
            />
            <small v-if="file" class="text-green-600 mt-2 block">
              📄 Selected: <strong>{{ file.name }}</strong>
            </small>
          </div>
          
          <Button
            @click="handleUpload"
            :disabled="!file || loading"
            :loading="loading"
            loadingIcon="pi pi-spin pi-search"
            class="px-8 py-4 text-lg font-bold"
            size="large"
          >
            {{ loading ? '🔍 Analyzing Drawing...' : '🚀 Analyze & Generate Cutting List' }}
          </Button>
        </div>
      </Panel>

      <!-- Error Display -->
      <Message 
        v-if="error" 
        severity="error" 
        :closable="false" 
        class="mb-8"
      >
        <template #messageicon>
          <i class="pi pi-exclamation-triangle"></i>
        </template>
        <div>
          <h3 class="font-bold mt-0 mb-1">Error Processing Drawing</h3>
          <p class="m-0">{{ error }}</p>
        </div>
      </Message>

      <!-- Loading State -->
      <Panel v-if="loading" class="mb-8">
        <div class="text-center">
          <ProgressSpinner class="mb-4" />
          <h3 class="text-xl font-bold text-primary mb-2">🔍 Analyzing Technical Drawing</h3>
          <p class="text-color-secondary mb-2">Extracting dimensions and analyzing cabinet structure...</p>
          <div class="text-sm text-color-secondary">
            <p class="mb-1">• Reading dimensional annotations</p>
            <p class="mb-1">• Identifying cabinet components</p>
            <p class="mb-0">• Generating optimized cutting list</p>
          </div>
        </div>
      </Panel>

      <!-- Results -->
      <div v-if="data">
        <!-- Analysis Summary -->
        <Panel class="mb-8">
          <template #header>
            <div class="flex justify-content-between align-items-center w-full">
              <div class="flex align-items-center gap-3">
                <i class="pi pi-chart-bar text-2xl"></i>
                <span class="text-2xl font-bold">DRAWING ANALYSIS SUMMARY</span>
              </div>
              <Button
                @click="showRawText = !showRawText"
                :label="showRawText ? '👁️ Hide Extracted Text' : '🔍 Show Extracted Text'"
                text
                size="small"
              />
            </div>
          </template>

          <div class="grid">
            <div class="col-12 md:col-6 lg:col-3">
              <Card class="bg-green-500 text-white text-center h-full">
                <template #content>
                  <div class="text-4xl font-bold mb-2">{{ totalPieces }}</div>
                  <div class="text-sm font-medium opacity-80">TOTAL COMPONENTS</div>
                </template>
              </Card>
            </div>
            <div class="col-12 md:col-6 lg:col-3">
              <Card class="bg-blue-500 text-white text-center h-full">
                <template #content>
                  <div class="text-4xl font-bold mb-2">{{ activeCategories }}</div>
                  <div class="text-sm font-medium opacity-80">COMPONENT TYPES</div>
                </template>
              </Card>
            </div>
            <div class="col-12 md:col-6 lg:col-3">
              <Card class="bg-purple-500 text-white text-center h-full">
                <template #content>
                  <div class="text-4xl font-bold mb-2">{{ totalMaterialArea }}</div>
                  <div class="text-sm font-medium opacity-80">TOTAL AREA (m²)</div>
                </template>
              </Card>
            </div>
            <div class="col-12 md:col-6 lg:col-3">
              <Card class="bg-orange-500 text-white text-center h-full">
                <template #content>
                  <div class="text-4xl font-bold mb-2">✓</div>
                  <div class="text-sm font-medium opacity-80">ANALYSIS COMPLETE</div>
                </template>
              </Card>
            </div>
          </div>

          <Message 
            v-if="data.analysis_type" 
            severity="info" 
            :closable="false" 
            class="mt-6"
          >
            <strong>Analysis Type:</strong> {{ data.analysis_type.replace('_', ' ').toUpperCase() }}
          </Message>
        </Panel>

        <!-- Raw Text Display -->
        <Panel v-if="showRawText && data.raw_text" class="mb-8">
          <template #header>
            <div class="flex align-items-center gap-3">
              <i class="pi pi-file-word text-2xl"></i>
              <span class="text-2xl font-bold">Extracted Text Data</span>
            </div>
          </template>
          <pre class="bg-gray-50 p-4 border-round text-sm text-color whitespace-pre-wrap border-1 surface-border">{{ data.raw_text }}</pre>
        </Panel>

        <!-- Generated Cutting List -->
        <Panel class="mb-8">
          <template #header>
            <div>
              <h2 class="text-3xl font-bold mb-2 mt-0">📋 GENERATED CUTTING LIST</h2>
              <p class="text-color-secondary m-0">Automatically generated from technical drawing analysis</p>
            </div>
          </template>

          <!-- Cutting List Sections -->
          <div v-if="data.categories && Object.keys(data.categories).length > 0">
            <div v-for="[categoryName, categoryData] in Object.entries(data.categories)" :key="categoryName">
              <CuttingListSection
                :categoryName="categoryName"
                :categoryData="categoryData"
              />
            </div>

            <!-- Grand Total -->
            <Card class="bg-green-500 text-white mt-8">
              <template #content>
                <div class="flex justify-content-between align-items-center">
                  <div>
                    <h3 class="text-2xl font-bold mt-0 mb-2">🎯 PROJECT TOTALS</h3>
                    <p class="opacity-80 m-0">Complete cutting list summary</p>
                  </div>
                  <div class="text-right">
                    <div class="text-4xl font-bold">{{ totalPieces }}</div>
                    <div class="text-sm opacity-80">TOTAL PIECES</div>
                    <div class="text-lg font-medium mt-2">{{ totalMaterialArea }} m²</div>
                    <div class="text-xs opacity-80">MATERIAL AREA</div>
                  </div>
                </div>
              </template>
            </Card>

            <!-- Export Options -->
            <Panel class="mt-8">
              <template #header>
                <div class="flex align-items-center gap-3">
                  <i class="pi pi-download text-xl"></i>
                  <span class="text-xl font-bold">Export Options</span>
                </div>
              </template>
              <div class="flex flex-wrap gap-3">
                <Button icon="pi pi-clipboard" label="Copy to Clipboard" />
                <Button icon="pi pi-file-excel" label="Export to Excel" severity="success" />
                <Button icon="pi pi-file-pdf" label="Export to PDF" severity="danger" />
                <Button icon="pi pi-print" label="Print Cutting List" severity="help" />
              </div>
            </Panel>
          </div>

          <div v-else class="text-center text-color-secondary p-8">
            <i class="pi pi-file-o text-6xl mb-4 block"></i>
            <h3 class="text-xl font-bold mb-2">No Components Found</h3>
            <p class="m-0">The drawing analysis did not identify any cabinet components. Please check that your image contains dimensional information.</p>
          </div>
        </Panel>

        <!-- Additional Information -->
        <Panel>
          <template #header>
            <div class="flex align-items-center gap-3">
              <i class="pi pi-info-circle text-xl"></i>
              <span class="text-xl font-bold">Analysis Information</span>
            </div>
          </template>
          <div class="grid">
            <div class="col-12 md:col-6">
              <Message severity="info" :closable="false">
                <template #messageicon>
                  <i class="pi pi-cog"></i>
                </template>
                <div>
                  <h4 class="font-bold mb-2 mt-0">Processing Details</h4>
                  <ul class="text-sm m-0 pl-4">
                    <li>• Image processed using OCR technology</li>
                    <li>• Dimensions extracted and validated</li>
                    <li>• Components categorized by type</li>
                    <li>• Quantities calculated automatically</li>
                  </ul>
                </div>
              </Message>
            </div>
            <div class="col-12 md:col-6">
              <Message severity="warn" :closable="false">
                <template #messageicon>
                  <i class="pi pi-exclamation-triangle"></i>
                </template>
                <div>
                  <h4 class="font-bold mb-2 mt-0">⚠️ Important Notes</h4>
                  <ul class="text-sm m-0 pl-4">
                    <li>• Always verify dimensions manually</li>
                    <li>• Check material specifications</li>
                    <li>• Account for material wastage</li>
                    <li>• Consider grain direction requirements</li>
                  </ul>
                </div>
              </Message>
            </div>
          </div>
        </Panel>
      </div>
    </div>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-8 mt-8">
      <div class="container mx-auto px-6 text-center">
        <div class="text-2xl font-bold mb-2">🏗️ Technical Drawing Analyzer</div>
        <p class="text-gray-400 text-sm mb-4">
          Professional Cabinet Making Tool • Blueprint Analysis • Automated Cutting Lists
        </p>
        <div class="text-xs text-gray-500">
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
.container {
  max-width: 1200px;
}

.bg-primary {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
}

.text-primary-color {
  color: white;
}

.text-primary-100 {
  color: rgba(255, 255, 255, 0.7);
}

.bg-green-500 {
  background: #4caf50;
}

.bg-blue-500 {
  background: #2196f3;
}

.bg-purple-500 {
  background: #9c27b0;
}

.bg-orange-500 {
  background: #ff9800;
}

pre {
  font-family: 'Courier New', monospace;
  overflow-x: auto;
}

footer {
  background-color: #2c3e50;
}
</style>