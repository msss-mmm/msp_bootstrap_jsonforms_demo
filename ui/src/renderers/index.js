import { rankWith, isStringControl, isNumberControl, isBooleanControl, isDateControl, isTimeControl, isLayout, isGroup, uiTypeIs, isControl } from '@jsonforms/core'
import { vanillaRenderers } from '@jsonforms/vue-vanilla'
import StringControlRenderer from './StringControlRenderer.vue'
import NumberControlRenderer from './NumberControlRenderer.vue'
import BooleanControlRenderer from './BooleanControlRenderer.vue'
import DateControlRenderer from './DateControlRenderer.vue'
import TimeControlRenderer from './TimeControlRenderer.vue'
import RadioControlRenderer from './RadioControlRenderer.vue'
import MultiSelectControlRenderer from './MultiSelectControlRenderer.vue'
import VerticalLayoutRenderer from './VerticalLayoutRenderer.vue'
import HorizontalLayoutRenderer from './HorizontalLayoutRenderer.vue'
import GroupLayoutRenderer from './GroupLayoutRenderer.vue'
import ApprovalControlRenderer from './ApprovalControlRenderer.vue'
import TimerControlRenderer from './TimerControlRenderer.vue'
import CaptureControlRenderer from './CaptureControlRenderer.vue'
import TitleControlRenderer from './TitleControlRenderer.vue'
import DocumentTypeControlRenderer from './DocumentTypeControlRenderer.vue'
import MixtureRecordNumberControlRenderer from './MixtureRecordNumberControlRenderer.vue'
import ReadOnlyControlRenderer from './ReadOnlyControlRenderer.vue'

const isApprovalControl = (uischema) => {
  return isControl(uischema) && (uischema.options?.type === 'OperatorApprove' || uischema.options?.type === 'QAApprove')
}

const isRadioControl = (uischema) => {
  return isControl(uischema) && uischema.options?.format === 'radio'
}

const isMultiSelectControl = (uischema) => {
  return isControl(uischema) && uischema.options?.format === 'multi-select'
}
const isTimerControl = (uischema) => {
  return isControl(uischema) && uischema.options?.type === 'Timer'
}
const isExternalCaptureControl = (uischema) => {
  return isControl(uischema) && uischema.options?.type === 'ExternalCapture'
}

const isTitleControl = (uischema) => {
  return isControl(uischema) && uischema.options?.type === 'Title'
}

const isDocumentTypeControl = (uischema) => {
  return isControl(uischema) && uischema.options?.type === 'DocumentType'
}

const isMixtureRecordNumberControl = (uischema) => {
  return isControl(uischema) && uischema.options?.type === 'MixtureRecordNumber'
}

export const elementRenderers = [
  ...vanillaRenderers,
  { tester: rankWith(100, isApprovalControl), renderer: ApprovalControlRenderer },
   { tester: rankWith(25, isRadioControl), renderer: RadioControlRenderer },
   { tester: rankWith(25, isMultiSelectControl), renderer: MultiSelectControlRenderer },
  { tester: rankWith(100, isTimerControl), renderer: TimerControlRenderer },
  { tester: rankWith(100, isExternalCaptureControl), renderer: CaptureControlRenderer },
  { tester: rankWith(100, isTitleControl), renderer: TitleControlRenderer },
  { tester: rankWith(100, isDocumentTypeControl), renderer: DocumentTypeControlRenderer },
  { tester: rankWith(100, isMixtureRecordNumberControl), renderer: MixtureRecordNumberControlRenderer },
   { tester: rankWith(10, isStringControl), renderer: StringControlRenderer },
   { tester: rankWith(20, isNumberControl), renderer: NumberControlRenderer },
   { tester: rankWith(20, isBooleanControl), renderer: BooleanControlRenderer },
   { tester: rankWith(20, isDateControl), renderer: DateControlRenderer },
   { tester: rankWith(20, isTimeControl), renderer: TimeControlRenderer },
  { tester: rankWith(10, uiTypeIs('VerticalLayout')), renderer: VerticalLayoutRenderer },
  { tester: rankWith(10, uiTypeIs('HorizontalLayout')), renderer: HorizontalLayoutRenderer },
  { tester: rankWith(10, isGroup), renderer: GroupLayoutRenderer }
]

export const readOnlyRenderers = [
  ...vanillaRenderers,
  { tester: rankWith(200, isApprovalControl), renderer: ApprovalControlRenderer },
  { tester: rankWith(200, isTimerControl), renderer: TimerControlRenderer },
  { tester: rankWith(200, isExternalCaptureControl), renderer: CaptureControlRenderer },
  { tester: rankWith(200, isTitleControl), renderer: TitleControlRenderer },
  { tester: rankWith(200, isDocumentTypeControl), renderer: DocumentTypeControlRenderer },
  { tester: rankWith(200, isMixtureRecordNumberControl), renderer: MixtureRecordNumberControlRenderer },
  { tester: rankWith(150, isControl), renderer: ReadOnlyControlRenderer },
  { tester: rankWith(10, uiTypeIs('VerticalLayout')), renderer: VerticalLayoutRenderer },
  { tester: rankWith(10, uiTypeIs('HorizontalLayout')), renderer: HorizontalLayoutRenderer },
  { tester: rankWith(10, isGroup), renderer: GroupLayoutRenderer }
]
