<template>
    <div class="panel" :style="{top: position.top, left: position.left}">
        <va-button v-for="(action, index) in actions" :color="action.color" :icon="action.icon"
                   preset="secondary" size="small"
                   @click="btnClick(index)" :disabled="!action.enabled" class="action-btn" />
    </div>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from "vue-facing-decorator";

@Component
class ActionsPanel extends Vue {
    @Prop actions: Array<any>
    @Prop position: { top: string, left: string }
    @Prop btnClick
}

export default toNative(ActionsPanel);

</script>

<style lang="scss" scoped>
.panel {
    position: absolute; /* Set parent position to relative */
    margin-left: 0; /* Initial margin */
    margin-top: 0; /* Initial margin */
    z-index: 10;
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
}

.action-btn {
    margin: 8px;
}
</style>