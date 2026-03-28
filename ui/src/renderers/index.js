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
  { tester: rankWith(3, isNumberControl), renderer: NumberControlRenderer },
  { tester: rankWith(3, isBooleanControl), renderer: BooleanControlRenderer },
  { tester: rankWith(3, isDateControl), renderer: DateControlRenderer },
  { tester: rankWith(3, isTimeControl), renderer: TimeControlRenderer }
]
