import sys
import pandas as pd

from aerovision.flight import Flight

class FlightParser:
	"""
	This class can parse flightdata files into pandas dataframes.

	"""

	def getFlights(self, dataFile):
		"""
		Returns a dictionary of all flights contained in the given dataFile.

		"""
		# Read dataFile into pandas dataframe
		flightsDF = self.readData(dataFile)

		# create a helper column that contains 1 if the icao24 changes compared to the previous row
		flightsDF['changed'] = flightsDF['icao24'].ne(flightsDF['icao24'].shift().bfill()).astype(int)

		# create a flightId column that increases value when a 1 occurs in the 'changed' column
		flightsDF['flightId'] = flightsDF['changed'].diff().eq(1).cumsum()

		# drop the helper column
		flightsDF = flightsDF.drop(columns='changed')

		# get a list of all unique flightIds
		flightIds = flightsDF.flightId.unique()

		# create a dictionary with a Flight object for each flight in flightsDF
		flights = dict()
		for flightId in flightIds:
			trajectory = flightsDF[:][flightsDF['flightId'] == flightId]

			# only use flights with enough data for spline interpolation
			if trajectory.shape[0] < 10:
				continue
			flights[str(flightId)] = Flight(trajectory)

		return flights

	def readData(self, dataFile):
		"""
		Read data of the given dataFile into a pandas dataframe.

		"""
		# read csv into a pandas dataframe
		flightsDF = pd.read_csv(dataFile)

		# remove erroneous data
		flightsDF = flightsDF[flightsDF.onground == False]
		flightsDF = flightsDF[flightsDF.alert == False]

		# clean data by removing sudden large altitude changes
		flightsDF = flightsDF[flightsDF.geoaltitude.diff() < 200]
		flightsDF = flightsDF[flightsDF.geoaltitude.diff() > -200]

		return flightsDF