<template>
  <div class="section-card">
    <div class="section-header">
      <div class="section-header-content">
        <i class="pi pi-table section-icon"></i>
        <span class="section-title">📋 CONSOLIDATED CUTTING LIST</span>
      </div>
      <div class="header-actions">
        <Button 
          icon="pi pi-download" 
          label="Export CSV" 
          size="small" 
          severity="secondary"
          @click="exportToCSV"
        />
        <Button 
          icon="pi pi-print" 
          label="Print" 
          size="small" 
          severity="info"
          @click="printTable"
        />
      </div>
    </div>

    <div class="consolidated-table-container">
      <DataTable 
        :value="consolidatedData" 
        class="consolidated-cutting-table"
        stripedRows
        responsiveLayout="scroll"
        :showGridlines="true"
        :paginator="consolidatedData.length > 20"
        :rows="20"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown"
        :rowsPerPageOptions="[10,20,50]"
        currentPageReportTemplate="Showing {first} to {last} of {totalRecords} parts"
        :globalFilterFields="['partName', 'materialType', 'notes']"
        ref="consolidatedTable"
      >
        <!-- Part ID/Name Column -->
        <Column 
          field="partName" 
          header="Part ID/Name" 
          :sortable="true"
          headerStyle="width: 180px; background-color: #1e293b; color: white; font-weight: bold;" 
          bodyStyle="font-weight: 600; padding: 12px;"
        >
          <template #body="slotProps">
            <div class="part-cell">
              <div class="part-id">{{ slotProps.data.partName }}</div>
              <div class="part-type">{{ slotProps.data.categoryShort }}</div>
            </div>
          </template>
        </Column>
        
        <!-- Width Column -->
        <Column 
          field="width" 
          header="Width (mm)" 
          :sortable="true"
          headerStyle="width: 120px; text-align: center; background-color: #1e293b; color: white; font-weight: bold;" 
          bodyStyle="text-align: center; font-family: 'Courier New', monospace; font-weight: 600; padding: 12px;"
        >
          <template #body="slotProps">
            <span class="dimension-cell">{{ slotProps.data.width }}</span>
          </template>
        </Column>
        
        <!-- Height Column -->
        <Column 
          field="height" 
          header="Height (mm)" 
          :sortable="true"
          headerStyle="width: 120px; text-align: center; background-color: #1e293b; color: white; font-weight: bold;" 
          bodyStyle="text-align: center; font-family: 'Courier New', monospace; font-weight: 600; padding: 12px;"
        >
          <template #body="slotProps">
            <span class="dimension-cell">{{ slotProps.data.height }}</span>
          </template>
        </Column>
        
        <!-- Quantity Column -->
        <Column 
          field="quantity" 
          header="Quantity" 
          :sortable="true"
          headerStyle="width: 100px; text-align: center; background-color: #1e293b; color: white; font-weight: bold;" 
          bodyStyle="text-align: center; padding: 12px;"
        >
          <template #body="slotProps">
            <Badge :value="slotProps.data.quantity" severity="warning" class="quantity-badge-large" />
          </template>
        </Column>
        
        <!-- Material Type Column -->
        <Column 
          field="materialType" 
          header="Material Type" 
          :sortable="true"
          headerStyle="width: 140px; background-color: #1e293b; color: white; font-weight: bold;" 
          bodyStyle="padding: 12px;"
        >
          <template #body="slotProps">
            <Tag :value="slotProps.data.materialType" :severity="getMaterialSeverity(slotProps.data.materialType)" />
          </template>
        </Column>
        
        <!-- Notes Column -->
        <Column 
          field="notes" 
          header="Notes" 
          headerStyle="background-color: #1e293b; color: white; font-weight: bold;" 
          bodyStyle="padding: 12px;"
        >
          <template #body="slotProps">
            <div class="notes-cell-consolidated">
              <div class="note-text">{{ slotProps.data.notes }}</div>
              <div class="note-meta">
                <span class="category-tag">{{ slotProps.data.category }}</span>
                <span class="dimensions-tag">{{ slotProps.data.width }}×{{ slotProps.data.height }}</span>
              </div>
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Summary Footer -->
    <div class="consolidated-footer">
      <div class="summary-stats">
        <div class="summary-item">
          <span class="summary-label">Total Parts:</span>
          <span class="summary-value">{{ totalParts }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">Categories:</span>
          <span class="summary-value">{{ uniqueCategories }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">Total Area:</span>
          <span class="summary-value">{{ totalArea }} m²</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">Material Types:</span>
          <span class="summary-value">{{ uniqueMaterials }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Badge from 'primevue/badge'
import Tag from 'primevue/tag'
import Button from 'primevue/button'

// Props
const props = defineProps({
  categories: {
    type: Object,
    required: true
  }
})

// Refs
const consolidatedTable = ref(null)

// Computed properties
const consolidatedData = computed(() => {
  const data = []
  let partCounter = 1
  
  Object.entries(props.categories).forEach(([categoryName, categoryData]) => {
    if (categoryData.items && categoryData.items.length > 0) {
      categoryData.items.forEach((item, index) => {
        for (let i = 0; i < item.quantity; i++) {
          data.push({
            partName: `${getCategoryShortName(categoryName)}-${String(partCounter).padStart(3, '0')}`,
            category: categoryName,
            categoryShort: getCategoryShortName(categoryName),
            width: item.width,
            height: item.height,
            quantity: 1, // Each row represents 1 piece
            materialType: getMaterialType(categoryName),
            notes: item.raw_text || `${categoryName} component`,
            area: (item.width * item.height) / 1000000 // m²
          })
          partCounter++
        }
      })
    }
  })
  
  return data.sort((a, b) => a.partName.localeCompare(b.partName))
})

const totalParts = computed(() => consolidatedData.value.length)

const uniqueCategories = computed(() => {
  return new Set(consolidatedData.value.map(item => item.category)).size
})

const uniqueMaterials = computed(() => {
  return new Set(consolidatedData.value.map(item => item.materialType)).size
})

const totalArea = computed(() => {
  return consolidatedData.value.reduce((sum, item) => sum + item.area, 0).toFixed(2)
})

// Methods
const getCategoryShortName = (category) => {
  const shortNames = {
    'GABLE': 'GAB',
    'T/B & FIX SHELVES': 'SHF',
    'BACKS': 'BCK',
    'S/H': 'SHH',
    'DRAWS': 'DRW',
    'END PANELS & INFILLS': 'PNL',
    'BRACES': 'BRC',
    'DOORS & DRAW FACES': 'DOR'
  }
  return shortNames[category] || 'CMP'
}

const getMaterialType = (category) => {
  const materials = {
    'GABLE': '18mm MFC',
    'T/B & FIX SHELVES': '18mm MFC',
    'BACKS': '6mm MDF',
    'S/H': '18mm MFC',
    'DRAWS': '12mm Ply',
    'END PANELS & INFILLS': '18mm MFC',
    'BRACES': '18mm MFC',
    'DOORS & DRAW FACES': '18mm MFC'
  }
  return materials[category] || '18mm MFC'
}

const getMaterialSeverity = (materialType) => {
  if (materialType.includes('18mm MFC')) return 'info'
  if (materialType.includes('12mm Ply')) return 'warning'
  if (materialType.includes('6mm MDF')) return 'secondary'
  return 'success'
}

const exportToCSV = () => {
  const headers = ['Part ID/Name', 'Width (mm)', 'Height (mm)', 'Quantity', 'Material Type', 'Notes']
  const csvContent = [
    headers.join(','),
    ...consolidatedData.value.map(row => [
      `"${row.partName}"`,
      row.width,
      row.height,
      row.quantity,
      `"${row.materialType}"`,
      `"${row.notes}"`
    ].join(','))
  ].join('\n')
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `cutting-list-${new Date().toISOString().split('T')[0]}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const printTable = () => {
  window.print()
}
</script>

<style scoped>
.consolidated-table-container {
  overflow-x: auto;
}

.consolidated-cutting-table {
  border: 2px solid #1e293b;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.consolidated-cutting-table :deep(.p-datatable-table) {
  border-collapse: collapse;
  width: 100%;
  min-width: 800px;
}

.consolidated-cutting-table :deep(.p-datatable-thead > tr > th) {
  background-color: #1e293b !important;
  color: white !important;
  border: 1px solid #374151;
  padding: 16px 12px;
  font-weight: 700;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.consolidated-cutting-table :deep(.p-datatable-tbody > tr > td) {
  border: 1px solid #e5e7eb;
  padding: 12px;
  vertical-align: middle;
  background-color: white;
}

.consolidated-cutting-table :deep(.p-datatable-tbody > tr:nth-child(even) > td) {
  background-color: #f9fafb;
}

.consolidated-cutting-table :deep(.p-datatable-tbody > tr:hover > td) {
  background-color: #f3f4f6 !important;
}

.part-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.part-id {
  font-weight: 700;
  color: #1f2937;
  font-size: 0.9rem;
}

.part-type {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 600;
  text-transform: uppercase;
}

.dimension-cell {
  font-weight: 700;
  color: #1f2937;
  font-size: 0.9rem;
}

.quantity-badge-large {
  font-weight: 700;
  min-width: 40px;
  font-size: 0.875rem;
}

.notes-cell-consolidated {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.note-text {
  color: #4b5563;
  font-size: 0.875rem;
  line-height: 1.4;
  margin-bottom: 4px;
}

.note-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.category-tag {
  background: #dbeafe;
  color: #1e40af;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.dimensions-tag {
  background: #f3f4f6;
  color: #374151;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  font-family: 'Courier New', monospace;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 2rem;
  background: linear-gradient(135deg, #f8fafc, #e2e8f0);
  border-bottom: 1px solid #e2e8f0;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
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

.consolidated-footer {
  background: linear-gradient(135deg, #1e293b, #374151);
  color: white;
  padding: 1.5rem 2rem;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.summary-label {
  font-weight: 600;
  font-size: 0.875rem;
  opacity: 0.9;
}

.summary-value {
  font-weight: 700;
  font-size: 1.1rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .header-actions {
    width: 100%;
  }
  
  .header-actions .p-button {
    flex: 1;
  }
  
  .consolidated-cutting-table :deep(.p-datatable-thead > tr > th),
  .consolidated-cutting-table :deep(.p-datatable-tbody > tr > td) {
    padding: 8px 6px;
    font-size: 0.75rem;
  }
  
  .part-id {
    font-size: 0.8rem;
  }
  
  .dimension-cell {
    font-size: 0.8rem;
  }
  
  .note-text {
    font-size: 0.75rem;
  }
  
  .summary-stats {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}

@media print {
  .section-header {
    background: white !important;
  }
  
  .consolidated-footer {
    background: white !important;
    color: black !important;
  }
  
  .summary-item {
    background: #f5f5f5 !important;
  }
  
  .consolidated-cutting-table :deep(.p-datatable-thead > tr > th) {
    background: #f5f5f5 !important;
    color: black !important;
  }
}
</style>