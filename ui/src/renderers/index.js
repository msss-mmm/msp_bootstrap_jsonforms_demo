import { rankWith, isStringControl, isNumberControl, isBooleanControl, isDateControl, isTimeControl } from '@jsonforms/core'
import { vanillaRenderers } from '@jsonforms/vue-vanilla'
import StringControlRenderer from './StringControlRenderer.vue'
import NumberControlRenderer from './NumberControlRenderer.vue'
import BooleanControlRenderer from './BooleanControlRenderer.vue'
import DateControlRenderer from './DateControlRenderer.vue'
import TimeControlRenderer from './TimeControlRenderer.vue'

export const elementRenderers = [
  ...vanillaRenderers,
  { tester: rankWith(3, isStringControl), renderer: StringControlRenderer },
  { tester: rankWith(4, isNumberControl), renderer: NumberControlRenderer },
  { tester: rankWith(4, isBooleanControl), renderer: BooleanControlRenderer },
  { tester: rankWith(4, isDateControl), renderer: DateControlRenderer },
  { tester: rankWith(4, isTimeControl), renderer: TimeControlRenderer }
]
