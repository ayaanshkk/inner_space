<template>
  <Panel v-if="categoryData.items.length > 0" class="mb-6">
    <template #header>
      <div class="flex justify-content-between align-items-center w-full">
        <h3 class="text-xl font-bold flex align-items-center gap-3 m-0">
          <span class="text-2xl">{{ getCategoryIcon(categoryName) }}</span>
          {{ categoryName }}
        </h3>
        <div class="flex gap-3">
          <Badge :value="categoryData.total_pieces + ' pieces'" severity="info" />
          <Badge :value="categoryData.unique_sizes + ' sizes'" severity="success" />
        </div>
      </div>
    </template>

    <DataTable 
      :value="categoryData.items" 
      class="p-datatable-sm custom-cutting-table"
      stripedRows
      responsiveLayout="scroll"
      :showGridlines="true"
    >
      <!-- Part ID/Name Column -->
      <Column header="Part ID/Name" headerStyle="width: 200px; background-color: #f8fafc; font-weight: bold;" bodyStyle="font-weight: 500;">
        <template #body="slotProps">
          <div class="part-name-cell">
            <div class="part-id">{{ categoryName }}-{{ String(slotProps.index + 1).padStart(2, '0') }}</div>
            <div class="part-category">{{ getCategoryShortName(categoryName) }}</div>
          </div>
        </template>
      </Column>
      
      <!-- Width Column -->
      <Column header="Width (mm)" headerStyle="width: 120px; text-align: center; background-color: #f8fafc; font-weight: bold;" bodyStyle="text-align: center;">
        <template #body="slotProps">
          <span class="dimension-value">{{ slotProps.data.width }}</span>
        </template>
      </Column>
      
      <!-- Height Column -->
      <Column header="Height (mm)" headerStyle="width: 120px; text-align: center; background-color: #f8fafc; font-weight: bold;" bodyStyle="text-align: center;">
        <template #body="slotProps">
          <span class="dimension-value">{{ slotProps.data.height }}</span>
        </template>
      </Column>
      
      <!-- Quantity Column -->
      <Column header="Quantity" headerStyle="width: 100px; text-align: center; background-color: #f8fafc; font-weight: bold;" bodyStyle="text-align: center;">
        <template #body="slotProps">
          <Badge :value="slotProps.data.quantity" severity="warning" class="quantity-badge" />
        </template>
      </Column>
      
      <!-- Material Type Column -->
      <Column header="Material Type" headerStyle="width: 150px; background-color: #f8fafc; font-weight: bold;">
        <template #body="slotProps">
          <span class="material-type">{{ getMaterialType(categoryName) }}</span>
        </template>
      </Column>
      
      <!-- Notes Column -->
      <Column header="Notes" headerStyle="background-color: #f8fafc; font-weight: bold;">
        <template #body="slotProps">
          <div class="notes-cell">
            <div class="note-description">{{ slotProps.data.raw_text }}</div>
            <div class="note-dimensions">{{ slotProps.data.dimensions }} mm</div>
          </div>
        </template>
      </Column>
    </DataTable>

    <!-- Section Total Row -->
    <div class="section-total-row">
      <div class="total-left">
        <span class="total-label">SUBTOTAL - {{ categoryName }}:</span>
      </div>
      <div class="total-right">
        <div class="total-pieces">
          <Badge :value="categoryData.total_pieces + ' pieces'" severity="info" class="total-badge" />
        </div>
        <div class="total-info">
          <small>{{ categoryData.unique_sizes }} unique dimensions</small>
          <small>{{ calculateTotalArea(categoryData.items) }} m² total area</small>
        </div>
      </div>
    </div>
  </Panel>
</template>

<script setup>
import Panel from 'primevue/panel'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Badge from 'primevue/badge'

// Props
const props = defineProps({
  categoryName: {
    type: String,
    required: true
  },
  categoryData: {
    type: Object,
    required: true
  }
})

// Methods
const getCategoryIcon = (category) => {
  const icons = {
    'GABLE': '📐',
    'T/B & FIX SHELVES': '📏',
    'BACKS': '🪟',
    'S/H': '📊',
    'DRAWS': '📦',
    'END PANELS & INFILLS': '🔳',
    'BRACES': '🔧',
    'DOORS & DRAW FACES': '🚪'
  }
  return icons[category] || '📋'
}

const getCategoryShortName = (category) => {
  const shortNames = {
    'GABLE': 'GABLE',
    'T/B & FIX SHELVES': 'SHELF',
    'BACKS': 'BACK',
    'S/H': 'SHELF_H',
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
    'S/H': '18mm MFC',
    'DRAWS': '12mm Ply',
    'END PANELS & INFILLS': '18mm MFC',
    'BRACES': '18mm MFC',
    'DOORS & DRAW FACES': '18mm MFC'
  }
  return materials[category] || '18mm MFC'
}

const calculateTotalArea = (items) => {
  let totalArea = 0
  items.forEach(item => {
    totalArea += (item.width * item.height * item.quantity) / 1000000 // Convert to m²
  })
  return totalArea.toFixed(2)
}
</script>

<style scoped>
.custom-cutting-table {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

.custom-cutting-table :deep(.p-datatable-table) {
  border-collapse: collapse;
}

.custom-cutting-table :deep(.p-datatable-thead > tr > th) {
  background-color: #f8fafc !important;
  border: 1px solid #d1d5db;
  padding: 12px 8px;
  font-weight: 700;
  color: #374151;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.custom-cutting-table :deep(.p-datatable-tbody > tr > td) {
  border: 1px solid #e5e7eb;
  padding: 12px 8px;
  vertical-align: middle;
}

.custom-cutting-table :deep(.p-datatable-tbody > tr:hover) {
  background-color: #f9fafb;
}

.part-name-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.part-id {
  font-weight: 600;
  color: #1f2937;
  font-size: 0.875rem;
}

.part-category {
  font-size: 0.75rem;
  color: #6b7280;
  text-transform: uppercase;
  font-weight: 500;
}

.dimension-value {
  font-weight: 600;
  color: #1f2937;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
}

.quantity-badge {
  font-weight: 700;
  min-width: 32px;
}

.material-type {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.notes-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.note-description {
  color: #4b5563;
  font-size: 0.875rem;
  line-height: 1.4;
}

.note-dimensions {
  color: #6b7280;
  font-size: 0.75rem;
  font-family: 'Courier New', monospace;
  font-weight: 500;
}

.section-total-row {
  background: linear-gradient(135deg, #f8fafc, #e2e8f0);
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 16px;
  margin-top: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.total-label {
  font-weight: 700;
  color: #1f2937;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.total-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.total-badge {
  font-size: 0.875rem;
  font-weight: 700;
}

.total-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.total-info small {
  color: #6b7280;
  font-size: 0.75rem;
  font-weight: 500;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .custom-cutting-table :deep(.p-datatable-thead > tr > th),
  .custom-cutting-table :deep(.p-datatable-tbody > tr > td) {
    padding: 8px 6px;
    font-size: 0.75rem;
  }
  
  .part-name-cell {
    gap: 1px;
  }
  
  .part-id {
    font-size: 0.75rem;
  }
  
  .part-category {
    font-size: 0.625rem;
  }
  
  .dimension-value {
    font-size: 0.75rem;
  }
  
  .material-type {
    font-size: 0.75rem;
  }
  
  .note-description {
    font-size: 0.75rem;
  }
  
  .note-dimensions {
    font-size: 0.625rem;
  }
  
  .section-total-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .total-right {
    width: 100%;
    justify-content: space-between;
  }
  
  .total-info {
    align-items: flex-start;
  }
}
</style>