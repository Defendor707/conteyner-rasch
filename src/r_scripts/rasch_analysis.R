#!/usr/bin/env Rscript

# Rasch modeli tahlili uchun R skripti
# Argument sifatida CSV fayl nomini oladi

args <- commandArgs(trailingOnly = TRUE)
if (length(args) == 0) {
  stop("CSV fayl nomi berilmagan")
}

input_file <- args[1]

# Kerakli kutubxonalarni yuklash
library(ltm)
library(ggplot2)
library(dplyr)

# Ma'lumotlarni o'qish
data <- read.csv(input_file)

# Talabgor ismi ustunini olib tashlash
data_matrix <- data[, !names(data) %in% c("student_name")]

# Faqat raqamli ustunlarni qoldirish
numeric_cols <- sapply(data_matrix, is.numeric)
data_matrix <- data_matrix[, numeric_cols]

# NaN qiymatlarni 0 ga almashtirish
data_matrix[is.na(data_matrix)] <- 0

# Faqat 0 va 1 qiymatlarini qoldirish
data_matrix[data_matrix != 0 & data_matrix != 1] <- 0

# Rasch modelini hisoblash (1PL)
tryCatch({
  if (ncol(data_matrix) > 1 && nrow(data_matrix) > 1) {
    rasch_model <- rasch(data_matrix)
    
    # Parametrlarni olish
    difficulty_params <- coef(rasch_model)[, "b"]
    ability_params <- factor.scores(rasch_model)$score.dat$z1
    
    # Model mosligini tekshirish
    model_fit <- gof(rasch_model)
    
    # Ishonchlilik koeffitsienti
    reliability <- cronbach.alpha(data_matrix)$alpha
    
    # Natijalarni chiqarish
    cat("=== RASCH MODELI NATIJALARI ===\n")
    cat("Qiyinlik parametrlari (b):\n")
    print(difficulty_params)
    
    cat("\nQobiliyat parametrlari (θ):\n")
    print(ability_params)
    
    cat("\nModel mosligi:\n")
    print(model_fit)
    
    cat("\nIshonchlilik koeffitsienti:\n")
    cat(reliability, "\n")
    
    # Rayt xaritasi yaratish
    wright_map <- create_wright_map(difficulty_params, ability_params)
    cat("\nRayt xaritasi yaratildi\n")
    
  } else {
    cat("Ma'lumotlar yetarli emas Rasch tahlili uchun\n")
    quit(status = 1)
  }
  
}, error = function(e) {
  cat("XATO:", e$message, "\n")
  quit(status = 1)
})

# Rayt xaritasi yaratish funksiyasi
create_wright_map <- function(difficulty, ability) {
  # Bu yerda Rayt xaritasi yaratish logikasi
  # Hozircha oddiy diagramma
  plot_data <- data.frame(
    type = c(rep("Savollar", length(difficulty)), rep("Talabgorlar", length(ability))),
    value = c(difficulty, ability)
  )
  
  p <- ggplot(plot_data, aes(x = type, y = value)) +
    geom_boxplot() +
    theme_minimal() +
    labs(title = "Rayt Xaritasi", x = "Tur", y = "Logit qiymati")
  
  ggsave("wright_map.png", p, width = 8, height = 6)
  return("wright_map.png")
}
