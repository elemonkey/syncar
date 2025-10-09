// Types for categories
export interface Category {
  id: number;
  importer_name: string;
  category_type: "medida" | "fabricante";
  name: string;
  url_param: string;
  created_at: string;
  updated_at: string;
}

export interface CategoryStats {
  importer_name: string;
  medida_count: number;
  fabricante_count: number;
  total_count: number;
  last_updated?: string;
}

export interface CategoryScrapeResult {
  importer_name: string;
  medida_count: number;
  fabricante_count: number;
  total_scraped: number;
  total_saved_db: number;
  deleted_old: number;
  success: boolean;
  message: string;
  execution_time?: string;
}

export interface CategoryImportResult {
  importer_name: string;
  medida_count: number;
  fabricante_count: number;
  total_imported: number;
  total_saved_db: number;
  deleted_old: number;
  success: boolean;
  message: string;
  execution_time?: string;
}