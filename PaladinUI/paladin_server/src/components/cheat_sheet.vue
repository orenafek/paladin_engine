<template>
  <div class="cheat-sheet-container">
    <va-button round icon="help" @click="btnClick" color="#eb6734"/>
    <div :class="{ 'cs': true, 'collapsed': !active }">
      <va-button round icon="help" @click="btnClick" v-if="active" color="#eb6734" />
      <div style="display: grid; justify-items: center;">
        <h3 class="cheat-sheet-header"> Cheat Sheet </h3>
        <code-editor :source-code="completions" lang="python" v-if="active"></code-editor>
      </div>
    </div>
  </div>

</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from "vue-facing-decorator";

//@ts-ignore
import CodeEditor from "./code-editor.vue";

@Component({
  components: {CodeEditor}
})
class CheatSheet extends Vue {

  @Prop completions: string

  active: boolean = false;

  mounted() {
    this.completions.replace('```', '');
  }

  btnClick() {
    this.active = !this.active;
  }
}

export default toNative(CheatSheet);

</script>

<style lang="scss" scoped>
.cs {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: 600px; /* Set your desired width */
  background-color: #2b2b2b;
  border-left: 1px solid #2b2b2b;
  box-shadow: -4px 0 5px -3px rgba(0, 0, 0, 0.4);
  transition: transform 0.3s ease-in-out;
}

.cheat-sheet-header {
  color: white;
}

.cs.collapsed {
  transform: translateX(100%);
}

.cheat-sheet-container {
  display: flex;
  justify-content: right;
  z-index: 999;
}

.toggle-button-wrapper {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  right: 0;
}

</style>