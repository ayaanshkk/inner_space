<template>
  <div class="cutting-list-container">
   <!-- Header - Only shown once at the top
    <div class="header-section">
      <h1>📋 GENERATED CUTTING LIST</h1>
      <p>Automatically generated from technical drawing analysis</p>
      <div class="header-badges">
        <span class="badge">{{ totalPieces }} total pieces</span>
        <span class="badge">{{ activeCategoriesCount }} categories</span>
      </div>
    </div> -->

    <!-- Categories -->
    <div v-if="hasData" class="categories-container">
      <div v-for="(categoryData, categoryName) in sortedCategories" :key="categoryName" class="category-section">
        <div v-if="categoryData.items && categoryData.items.length > 0" class="category-panel">
          <!-- Category Header - No main header here -->
          <div class="category-header">
            <h3>
              <span class="category-icon">{{ getCategoryIcon(categoryName) }}</span>
              {{ categoryName }}
            </h3>
            <div class="category-badges">
              <span class="badge-info">{{ categoryData.total_pieces || 0 }} pieces</span>
              <span class="badge-success">{{ categoryData.unique_sizes || 0 }} sizes</span>
            </div>
          </div>

          <!-- Items Table -->
          <div class="table-container">
            <table class="cutting-table">
              <thead>
                <tr>
                  <th>PART ID/NAME</th>
                  <th>WIDTH (MM)</th>
                  <th>HEIGHT (MM)</th>
                  <th>QUANTITY</th>
                  <th>MATERIAL TYPE</th>
                  <th>NOTES</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in categoryData.items" :key="index">
                  <td>
                    <div class="part-name">
                      <div class="part-id">{{ categoryName }}-{{ String(index + 1).padStart(2, '0') }}</div>
                      <div class="part-type">{{ getCategoryShortName(categoryName) }}</div>
                    </div>
                  </td>
                  <td class="dimension">{{ item.width }}</td>
                  <td class="dimension">{{ item.height }}</td>
                  <td class="quantity">
                    <span class="quantity-badge">{{ item.quantity }}</span>
                  </td>
                  <td class="material">{{ getMaterialType(categoryName) }}</td>
                  <td class="notes">
                    <div class="note-text">{{ item.raw_text }}</div>
                    <div class="note-dims">{{ item.dimensions }} mm</div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Subtotal -->
          <div class="subtotal-row">
            <span class="subtotal-label">SUBTOTAL - {{ categoryName }}:</span>
            <div class="subtotal-info">
              <span class="badge-info">{{ categoryData.total_pieces }} pieces</span>
              <div class="subtotal-details">
                <small>{{ categoryData.unique_sizes }} unique dimensions</small>
                <small>{{ calculateTotalArea(categoryData.items) }} m² total area</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- No Data Message -->
    <div v-else class="no-data">
      <p>No cutting list data available. Please upload a technical drawing to generate the cutting list.</p>
    </div>

    <!-- Summary
    <div v-if="totalPieces > 0" class="summary-section">
      <h3>📊 OVERALL SUMMARY</h3>
      <div class="summary-grid">
        <div class="summary-card">
          <div class="summary-icon">🔢</div>
          <h4>Total Pieces</h4>
          <div class="summary-number">{{ totalPieces }}</div>
        </div>
        <div class="summary-card">
          <div class="summary-icon">📂</div>
          <h4>Active Categories</h4>
          <div class="summary-number">{{ activeCategoriesCount }}</div>
        </div>
        <div class="summary-card">
          <div class="summary-icon">📐</div>
          <h4>Total Area</h4>
          <div class="summary-number">{{ totalArea }} m²</div>
        </div>
        <div class="summary-card">
          <div class="summary-icon">📏</div>
          <h4>Unique Sizes</h4>
          <div class="summary-number">{{ totalUniqueSizes }}</div>
        </div>
      </div>
    </div> -->

    <!-- Debug Panel -->
    <div v-if="debugMode" class="debug-panel">
      <h3>🐛 Debug Information</h3>
      <div class="debug-content">
        <h4>Categories Overview:</h4>
        <ul>
          <li v-for="(data, name) in allCategoriesData" :key="name">
            <strong>{{ name }}:</strong> {{ data.total_pieces || 0 }} pieces, {{ data.unique_sizes || 0 }} sizes
          </li>
        </ul>
        <!-- <details>
          <summary>Show Full Data Structure</summary>
          <pre>{{ JSON.stringify(allCategoriesData, null, 2) }}</pre>
        </details> -->
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

// Props
const props = defineProps({
  allCategoriesData: {
    type: Object,
    default: () => ({})
  },
  categoryName: {
    type: String,
    default: ''
  },
  categoryData: {
    type: Object,
    default: () => ({ items: [], total_pieces: 0, unique_sizes: 0 })
  },
  showEmptyCategories: {
    type: Boolean,
    default: false
  },
  debugMode: {
    type: Boolean,
    default: false
  }
})

// Computed properties
const finalCategoriesData = computed(() => {
  if (props.allCategoriesData && Object.keys(props.allCategoriesData).length > 0) {
    return props.allCategoriesData
  }
  
  if (props.categoryName && props.categoryData) {
    return {
      [props.categoryName]: props.categoryData
    }
  }
  
  return {}
})

const hasData = computed(() => {
  return Object.keys(finalCategoriesData.value).length > 0
})

const sortedCategories = computed(() => {
  const categoryOrder = [
    'GABLE',
    'T/B & FIX SHELVES',
    'BACKS', 
    'DOORS & DRAW FACES',
    'DRAWS',
    'S/H',
    'BRACES',
    'END PANELS & INFILLS'
  ]
  
  const sorted = {}
  
  categoryOrder.forEach(category => {
    if (finalCategoriesData.value[category]) {
      sorted[category] = finalCategoriesData.value[category]
    }
  })
  
  Object.keys(finalCategoriesData.value).forEach(category => {
    if (!sorted[category]) {
      sorted[category] = finalCategoriesData.value[category]
    }
  })
  
  return sorted
})

const totalPieces = computed(() => {
  return Object.values(finalCategoriesData.value).reduce((total, category) => {
    return total + (category.total_pieces || 0)
  }, 0)
})

const activeCategoriesCount = computed(() => {
  return Object.values(finalCategoriesData.value).filter(category => 
    category.total_pieces && category.total_pieces > 0
  ).length
})

const totalArea = computed(() => {
  let area = 0
  Object.values(finalCategoriesData.value).forEach(category => {
    if (category.items && category.items.length > 0) {
      category.items.forEach(item => {
        area += (item.width * item.height * item.quantity) / 1000000
      })
    }
  })
  return area.toFixed(2)
})

const totalUniqueSizes = computed(() => {
  return Object.values(finalCategoriesData.value).reduce((total, category) => {
    return total + (category.unique_sizes || 0)
  }, 0)
})

// Methods
const getCategoryIcon = (category) => {
  const icons = {
    'GABLE': '📐',
    'T/B & FIX SHELVES': '📏',
    'BACKS': '🪟',
    'S/H': '🔧',
    'DRAWS': '📦',
    'END PANELS & INFILLS': '🔳',
    'BRACES': '💪',
    'DOORS & DRAW FACES': '🚪'
  }
  return icons[category] || '📋'
}

const getCategoryShortName = (category) => {
  const shortNames = {
    'GABLE': 'GABLE',
    'T/B & FIX SHELVES': 'SHELF',
    'BACKS': 'BACK',
    'S/H': 'HARDWARE',
    'DRAWS': 'DRAWER',
    'END PANELS & INFILLS': 'PANEL',
    'BRACES': 'BRACE',
    'DOORS & DRAW FACES': 'DOOR'
  }
  return shortNames[category] || 'COMP'
}

const getMaterialType = (category) => {
  const materials = {
    'GABLE': '18mm MFC',
    'T/B & FIX SHELVES': '18mm MFC',
    'BACKS': '6mm MDF',
    'S/H': 'Hardware',
    'DRAWS': '12mm Ply',
    'END PANELS & INFILLS': '18mm MFC',
    'BRACES': '18mm MFC',
    'DOORS & DRAW FACES': '18mm MFC'
  }
  return materials[category] || '18mm MFC'
}

const calculateTotalArea = (items) => {
  if (!items || items.length === 0) return '0.00'
  
  let totalArea = 0
  items.forEach(item => {
    totalArea += (item.width * item.height * item.quantity) / 1000000
  })
  return totalArea.toFixed(2)
}
</script>

<style scoped>
.cutting-list-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header-section {
  background: linear-gradient(135deg, #f8fafc, #e2e8f0);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid #d1d5db;
}

.header-section h1 {
  font-size: 2rem;
  font-weight: bold;
  margin: 0 0 8px 0;
  color: #1f2937;
}

.header-section p {
  font-size: 1.125rem;
  color: #6b7280;
  margin: 0 0 16px 0;
}

.header-badges {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.badge {
  background: #3b82f6;
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
}

.categories-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.category-section {
  margin-bottom: 24px;
}

.category-panel {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.category-header {
  background: linear-gradient(135deg, #f8fafc, #f1f5f9);
  border-bottom: 1px solid #e2e8f0;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.category-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: bold;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 12px;
}

.category-icon {
  font-size: 1.5rem;
}

.category-badges {
  display: flex;
  gap: 12px;
}

.badge-info {
  background: #3b82f6;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-success {
  background: #10b981;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}

.table-container {
  overflow-x: auto;
}

.cutting-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.cutting-table th {
  background-color: #f8fafc;
  border: 1px solid #d1d5db;
  padding: 12px 8px;
  font-weight: 700;
  color: #374151;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  text-align: left;
}

.cutting-table td {
  border: 1px solid #e5e7eb;
  padding: 12px 8px;
  vertical-align: middle;
}

.cutting-table tbody tr:hover {
  background-color: #f9fafb;
}

.part-name {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.part-id {
  font-weight: 600;
  color: #1f2937;
  font-size: 0.875rem;
}

.part-type {
  font-size: 0.75rem;
  color: #6b7280;
  text-transform: uppercase;
  font-weight: 500;
}

.dimension {
  text-align: center;
  font-weight: 600;
  color: #1f2937;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
}

.quantity {
  text-align: center;
}

.quantity-badge {
  background: #f59e0b;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
  min-width: 24px;
  display: inline-block;
}

.material {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.notes {
  max-width: 200px;
}

.note-text {
  color: #4b5563;
  font-size: 0.875rem;
  line-height: 1.4;
  margin-bottom: 4px;
}

.note-dims {
  color: #6b7280;
  font-size: 0.75rem;
  font-family: 'Courier New', monospace;
  font-weight: 500;
}

.subtotal-row {
  background: linear-gradient(135deg, #f8fafc, #e2e8f0);
  border-top: 1px solid #d1d5db;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.subtotal-label {
  font-weight: 700;
  color: #1f2937;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.subtotal-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.subtotal-details {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.subtotal-details small {
  color: #6b7280;
  font-size: 0.75rem;
  font-weight: 500;
}

.no-data {
  background: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  color: #92400e;
}

.summary-section {
  background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
  border: 2px solid #0369a1;
  border-radius: 12px;
  padding: 24px;
  margin-top: 24px;
}

.summary-section h3 {
  margin: 0 0 20px 0;
  font-size: 1.25rem;
  font-weight: bold;
  color: #1f2937;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
}

.summary-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  border: 1px solid #e2e8f0;
}

.summary-icon {
  font-size: 2rem;
  margin-bottom: 8px;
}

.summary-card h4 {
  margin: 0 0 12px 0;
  color: #6b7280;
  font-size: 0.875rem;
  text-transform: uppercase;
  font-weight: 600;
}

.summary-number {
  font-size: 2.25rem;
  font-weight: 700;
  color: #1f2937;
}

.debug-panel {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 12px;
  padding: 20px;
  margin-top: 24px;
}

.debug-panel h3 {
  margin: 0 0 16px 0;
  font-size: 1.125rem;
  font-weight: bold;
}

.debug-content ul {
  margin: 0 0 16px 0;
  padding-left: 20px;
}

.debug-content li {
  margin-bottom: 4px;
}

.debug-content pre {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 12px;
  font-size: 12px;
  overflow-x: auto;
  font-family: 'Courier New', monospace;
}

/* Responsive */
@media (max-width: 768px) {
  .cutting-list-container {
    padding: 12px;
  }
  
  .header-section {
    padding: 16px;
  }
  
  .category-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .cutting-table th,
  .cutting-table td {
    padding: 8px 6px;
    font-size: 0.75rem;
  }
  
  .subtotal-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .subtotal-info {
    width: 100%;
    justify-content: space-between;
  }
  
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>