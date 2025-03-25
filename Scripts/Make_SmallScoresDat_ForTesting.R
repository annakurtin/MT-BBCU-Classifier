#### Load fake classifier outputs ####
library(data.table)
library(tidyverse)
library(janitor)



#### Load in scores ####
cnn_whole <- fread("D:/Test_Files_M2.0GUI/Test_Scores_Output/predictions_epoch-10_opso-0-10-1-2022_UMBEL_Audio.csv")
cn_orig <- copy(cnn_whole)
# Separate into point, date, time in order to sort and select them 
#cnn_whole %>% separate(file, into = c("root","point_id","filename"), sep = ("\\\\"))
cnn_whole[, c("root", "point_id", "filename") := tstrsplit(file, "\\\\")]
cnn_whole[, c("point_dup", "date", "hour_ext") := tstrsplit(filename, "_")]
cnn_whole[, c("hour", "ext") := tstrsplit(hour_ext, "\\.")]
# Select just a subset
cnn_sub <- cnn_whole[point_id %in% c("82-1","104-5","JUD-2")]
# Select the first three of each after grouping by point_id hour and date
cnn_sub <- cnn_sub[, .SD[1:3], by = .(point_id, hour, date)]
# Take just the first 
cnn_fortesting <- as.data.frame(cnn_sub[, 4:8])
write.csv(cnn_fortesting, "D:/Test_Files_M2.0GUI/Test_Scores_Output/predictions_2022_UMBEL_subset1.csv", row.names = FALSE)
