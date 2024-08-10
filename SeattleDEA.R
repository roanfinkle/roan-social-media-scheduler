library(tidyverse)

library(lpSolveAPI)
library(MultiplierDEA)

library(ucminf)
library(quadprog)
library(Benchmarking)

library(statnet.common)
library(sna)

library(ggplot2)

# change these as needed
all_data = read.csv('/Users/roanfinkle/Downloads/CRC/seattle_with_dummies.csv')
topic = 'entertainment'
sentiment = 'Positive_Sentiment'


# filters out boosted (Paid_Reach) posts
indexes = c()
for (i in 1:4517) {
  value = as.numeric(all_data[i,42])
  if ((is.na(value)) || (value != 0)) {
    indexes = c(indexes, i)
  }
}
all_data = all_data[-indexes,]


# avg sentiment for non binary inputs
avg_sent_vec = c()
for (i in 1:length(all_data[,1])) {
  avg_sent = (as.numeric(all_data[i,36]) + as.numeric(all_data[i,37])) / 2
  if (avg_sent > 1100) {
    avg_sent_vec = c(avg_sent_vec, 'Positive_Sentiment')
  } else if ((avg_sent <= 1100) && (avg_sent >= 900)) {
    avg_sent_vec = c(avg_sent_vec, 'Neutral_Sentiment')
  } else if (avg_sent < 900) {
    avg_sent_vec = c(avg_sent_vec, 'Negative_Sentiment')
  }
}
avg_sent_df = data.frame(avg_sent_vec)


# filters for given topic & sentiment
df = data.frame()
for (i in 1:length(all_data[,1])) {
  if ((all_data[i,35] == topic) && (avg_sent_df[i,1] == sentiment)) {
    df = rbind(df, all_data[i,])
  }
}


# filters out hour columns that contain all zero
all_zero = c()
for (i in 10:33) {
  if (all(df[,i] == 0)) {
    all_zero = c(all_zero, i)
  }
}


# authors & months can't be read in as factors, skip over these for now, also skip topics because it's filtered
# column 33 is Hour23
original_columns = c(1, 3:33)
input_columns = setdiff(original_columns, all_zero)
inputs = as.matrix(df[,input_columns])

# skip Photo_Views, Video_Plays, Paid_Reach, Paid_Impressions
# column 39 is Engagement
output_columns = c(1, 39:41, 43:49, 52:58, 60:64)
outputs = as.matrix(df[,output_columns])

# converts to numeric
inputs = apply(inputs, 2, as.numeric)
outputs = apply(outputs, 2, as.numeric)

# sets row name to DMU value
rownames(inputs) <- df %>% pull(DMU)
rownames(outputs) <- df %>% pull(DMU)


# initialize DEA model object
dea_obj = dea(
  X = inputs, #Input matrix
  Y = outputs, #Output matrix
  RTS = "vrs", #Returns to scale assumption (Variable returns to scale here)
  ORIENTATION = "out", #Compute output efficiency
  SLACK = T, #Compute slacks
  DUAL = T, #Compute dual matrices
  #CONTROL = list(epsint='1')
)

# computes DMU efficiency table
efficiencies <- tibble(
  DMU = df %>% pull(DMU), #DMU name column
  eff = (1 / eff(dea_obj) * 100) %>% round(4)   #Efficiencies (after scale conversion and rounding)
)

# plots efficiency frontier
dea.plot(
  x = inputs, #Input matrix
  y = outputs, #Output matrix
  RTS = "vrs", #Returns to scale assumption (Variable returns to scale here)
  ORIENTATION = "out", #Compute output efficiency
  txt = TRUE,  #Adds DMU number to points
  xlab = '',
  ylab = ''
)
title(main='Positive Entertainment Topic Frontier')
# ^^ change the title as needed

# computes weight variables
weights <- dea_obj$ux %>% round(8) %>% as_tibble()
colnames(weights) <- colnames(inputs) #Set names of inputs
weights$DMU = df$DMU

# computes slack variables
slacks <- dea_obj$sx %>% round(8) %>% as_tibble() 
colnames(slacks) <- colnames(inputs) #Set names of inputs
slacks$DMU = df$DMU

# computes peers
peers_matrix = dea_obj$lambda
colnames(peers_matrix) <- rownames(dea_obj$ux) #Set names of DMUs
rownames(peers_matrix) <- rownames(dea_obj$ux) #Set names of DMUs
peers = peers_matrix %>% as_tibble() %>% 
  mutate(across(where(is.numeric), ~round(.x, 2)))
rownames(peers) <- df %>% pull(DMU)

# gets rid of error5/na entries, then displays relevant scores
peers_df = data.frame(peers)
rownames(peers_df) = rownames(peers)
colnames(peers_df) = colnames(peers)
drop = c()
for (i in 1:length(peers_df[,1])) {
  if (is.na(peers_df[i,1])) {
    drop = c(drop, i)
  }
}
peers_df = peers_df[-drop,]

for (i in 1:length(peers_df[,1])) {
  for (j in 1:length(peers_df[1,])) {
    if ((as.numeric(peers_df[i,j]) != 0) && (as.numeric(peers_df[i,j]) != 1)) {
      temp = paste0('rowDMU:', rownames(peers_df)[i],' colDMU:', colnames(peers_df)[j], ' score:', peers_df[i,j])
      print(temp)
    }
  }
}

