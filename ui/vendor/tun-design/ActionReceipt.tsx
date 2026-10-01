'use client';
import { useId } from 'react';
import { displayTimestamp, effectiveReceiptStatus, parseTimestamp, receiptLabels,
  recoveryLabels, safeDetailsUrl, type ReceiptData } from './contracts.js';

export interface ActionReceiptProps { receipt: ReceiptData; className?: string }
/** Render a supplied record; never invent timestamps, completion, or undo capability. */
export function ActionReceipt({ receipt, className = '' }: ActionReceiptProps) {
  const id = useId();
  const status = effectiveReceiptStatus(receipt);
  const url = safeDetailsUrl(receipt.detailsUrl);
  const timestamp = parseTimestamp(receipt.timestamp);
  const tone = status === 'completed' ? 'success' : status === 'failed' ? 'danger'
    : status === 'partially-completed' || status === 'pending-verification' ? 'warning' : 'neutral';
  return <section className={`tun-component tun-receipt ${className}`} aria-labelledby={`${id}-title`}>
    <div className="tun-row tun-row-top">
      <div><p className="tun-eyebrow">Action receipt · application record</p><h2 className="tun-heading" id={`${id}-title`}>{receipt.action}</h2></div>
      <p className={`tun-badge tun-tone-${tone}`} role="status">{receiptLabels[status]}</p>
    </div>
    <p>{receipt.summary}</p>
    <dl className="tun-facts">
      <div><dt>Actor</dt><dd>{receipt.actor.name} ({receipt.actor.type})</dd></div>
      <div><dt>Target</dt><dd>{receipt.target}</dd></div>
      <div><dt>Recorded at</dt><dd>{timestamp === null ? 'Time unavailable' : <time dateTime={receipt.timestamp}>{displayTimestamp(receipt.timestamp)}</time>}</dd></div>
      <div><dt>Verification</dt><dd>{receipt.verification.detail || 'No verification evidence supplied.'}</dd></div>
      <div><dt>Recovery</dt><dd><strong>{recoveryLabels[receipt.recovery.kind]}.</strong> {receipt.recovery.description}</dd></div>
    </dl>
    <p className="tun-caption">Receipt {receipt.id}</p>
    {url && <a className="tun-link" href={url}>Inspect action record</a>}
    {receipt.detailsUrl && !url && <p className="tun-caption">The action-record link is unavailable.</p>}
  </section>;
}
