<template>
  <pre v-highlightjs><code class="python" v-text="code"></code></pre>
</template>

<script>
export default {
  name: "Highlighted",
  props: ['code'],
  methods: {}
}

const escapeTags = function (element) {
  console.log('e = '+element);
  if(typeof (element) == HTMLSpanElement){

  }
  element.innerHTML = element.innerHTML
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
}

export const escapeHTMLTags = function () {
  const observer = new MutationObserver(function (mutationsList, observer) {
    for (const mutation of mutationsList) {
      console.log('m = ' + mutation);
      if (mutation.type === 'childList') {
        mutation.addedNodes.forEach(node => {
          console.log('n = ' + node + ' nt = ' + typeof (node));
          node.childNodes.forEach(element => escapeTags(element));
        });
      }
    }
  });

  //observer.observe(document, {attributes: true, childList: true, subtree: true});
}


</script>

<style scoped>

</style>