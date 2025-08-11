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
      class="p-datatable-sm"
      stripedRows
      responsiveLayout="scroll"
    >
      <Column header="Item #" headerStyle="width: 80px; text-align: center;" bodyStyle="text-align: center;">
        <template #body="slotProps">
          <strong>{{ slotProps.index + 1 }}</strong>
        </template>
      </Column>
      
      <Column field="dimensions" header="Dimensions (W×H)" headerStyle="width: 180px;">
        <template #body="slotProps">
          <code class="text-lg font-bold text-primary">{{ slotProps.data.dimensions }}</code>
        </template>
      </Column>
      
      <Column field="width" header="Width (mm)" headerStyle="width: 120px;" bodyStyle="text-align: center;">
        <template #body="slotProps">
          <span class="font-medium">{{ slotProps.data.width }}</span>
        </template>
      </Column>
      
      <Column field="height" header="Height (mm)" headerStyle="width: 120px;" bodyStyle="text-align: center;">
        <template #body="slotProps">
          <span class="font-medium">{{ slotProps.data.height }}</span>
        </template>
      </Column>
      
      <Column header="Qty" headerStyle="width: 80px; text-align: center;" bodyStyle="text-align: center;">
        <template #body="slotProps">
          <Badge :value="slotProps.data.quantity" severity="warning" />
        </template>
      </Column>
      
      <Column field="raw_text" header="Description">
        <template #body="slotProps">
          <small class="text-color-secondary">{{ slotProps.data.raw_text }}</small>
        </template>
      </Column>
    </DataTable>

    <!-- Section Total Row -->
    <div class="bg-primary-50 border-primary-200 border-1 border-round p-3 mt-3 flex justify-content-between align-items-center">
      <span class="font-bold text-primary">
        SUBTOTAL - {{ categoryName }}:
      </span>
      <div class="flex align-items-center gap-4">
        <Badge :value="categoryData.total_pieces" severity="info" class="text-lg font-bold" />
        <small class="text-color-secondary">{{ categoryData.unique_sizes }} unique dimensions</small>
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
</script>

<style scoped>
code {
  font-family: 'Courier New', monospace;
}

/* Custom styles for badges in larger size */
.text-lg .p-badge {
  font-size: 1rem;
  padding: 0.5rem 0.75rem;
}
</style>