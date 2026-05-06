export interface DataSource {
  id: number; name: string; slug: string; description: string
  file_count: number; total_size: number
  tags: string[]; likes: number; is_active: boolean
  created_at: string; updated_at: string
}

export interface DatasetFile {
  id: number; source_id: number; file_name: string
  file_format: string; file_type: string; file_size: number
  schema_definition: Record<string, any>
  record_count: number; columns: string[]
  sort_order: number; created_at: string
}

export interface TabularPreview {
  type: "tabular"; file_name: string; format: string
  columns: string[]; total_rows: number
  preview: { row_index: number; data: Record<string, any> }[]
}

export interface RawPreview {
  type: "raw"; file_name: string; format: string
  file_size: number; total_lines: number
  preview_lines: string[]
}

export type FilePreview = TabularPreview | RawPreview

export interface ActivityLog {
  id: number
  action: string
  target_type: string | null
  target_id: number | null
  source_id: number | null
  source_name: string | null
  detail: string
  status: string  // success / failed
  created_at: string
}
