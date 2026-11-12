import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DecimalPipe } from '@angular/common';
import { report, groupSize, csvReport, PERIOD, VERSION } from './demand-demo';
@Component({
  selector: 'app-demand-synthetic',
  imports: [FormsModule, DecimalPipe],
  templateUrl: './demand-synthetic.html',
})
export class DemandSynthetic {
  readonly period = PERIOD;
  readonly version = VERSION;
  readonly semesters = Array.from({ length: 10 }, (_, i) => i + 1);
  filters = { query: '', semester: '', priority: '', order: 'descending' };
  referenceSize: number | null = null;
  get stats() {
    return report(this.filters);
  }
  get size() {
    return groupSize(this.referenceSize);
  }
  groups(total: number) {
    return this.size ? Math.ceil(total / this.size) : null;
  }
  exportCsv() {
    const url = URL.createObjectURL(
      new Blob([csvReport(this.stats, this.size, this.filters)], {
        type: 'text/csv;charset=utf-8',
      }),
    );
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'PREVIA-demanda-sintetica.csv';
    anchor.click();
    URL.revokeObjectURL(url);
  }
}
