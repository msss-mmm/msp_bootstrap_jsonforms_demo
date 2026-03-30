import { rankWith, isStringControl, isNumberControl, isBooleanControl, isDateControl, isTimeControl, isLayout, isGroup, uiTypeIs, isControl } from '@jsonforms/core'
import { vanillaRenderers } from '@jsonforms/vue-vanilla'
import StringControlRenderer from './StringControlRenderer.vue'
import NumberControlRenderer from './NumberControlRenderer.vue'
import BooleanControlRenderer from './BooleanControlRenderer.vue'
import DateControlRenderer from './DateControlRenderer.vue'
import TimeControlRenderer from './TimeControlRenderer.vue'
import VerticalLayoutRenderer from './VerticalLayoutRenderer.vue'
import HorizontalLayoutRenderer from './HorizontalLayoutRenderer.vue'
import GroupLayoutRenderer from './GroupLayoutRenderer.vue'
import ApprovalControlRenderer from './ApprovalControlRenderer.vue'
import ReadOnlyControlRenderer from './ReadOnlyControlRenderer.vue'

const isApprovalControl = (uischema) => {
  return isControl(uischema) && (uischema.options?.type === 'OperatorApprove' || uischema.options?.type === 'QAApprove')
}

export const elementRenderers = [
  ...vanillaRenderers,
  { tester: rankWith(100, isApprovalControl), renderer: ApprovalControlRenderer },
  { tester: rankWith(3, isStringControl), renderer: StringControlRenderer },
  { tester: rankWith(3, isNumberControl), renderer: NumberControlRenderer },
  { tester: rankWith(3, isBooleanControl), renderer: BooleanControlRenderer },
  { tester: rankWith(3, isDateControl), renderer: DateControlRenderer },
  { tester: rankWith(3, isTimeControl), renderer: TimeControlRenderer },
  { tester: rankWith(10, uiTypeIs('VerticalLayout')), renderer: VerticalLayoutRenderer },
  { tester: rankWith(10, uiTypeIs('HorizontalLayout')), renderer: HorizontalLayoutRenderer },
  { tester: rankWith(10, isGroup), renderer: GroupLayoutRenderer }
]

export const readOnlyRenderers = [
  ...vanillaRenderers,
  { tester: rankWith(200, isApprovalControl), renderer: ApprovalControlRenderer },
  { tester: rankWith(150, isControl), renderer: ReadOnlyControlRenderer },
  { tester: rankWith(10, uiTypeIs('VerticalLayout')), renderer: VerticalLayoutRenderer },
  { tester: rankWith(10, uiTypeIs('HorizontalLayout')), renderer: HorizontalLayoutRenderer },
  { tester: rankWith(10, isGroup), renderer: GroupLayoutRenderer }
]
