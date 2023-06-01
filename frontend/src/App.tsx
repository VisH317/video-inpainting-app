import React, { useState } from 'react'
import { Button, StatusBar, Text, useColorScheme, View, StyleSheet } from 'react-native'
import { NavigationContainer, createNavigationContainerRef } from '@react-navigation/native';
// import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createDrawerNavigator } from '@react-navigation/drawer';

import { launchImageLibrary } from 'react-native-image-picker'
import { gestureHandlerRootHOC, GestureHandlerRootView } from 'react-native-gesture-handler'
import { Colors } from 'react-native/Libraries/NewAppScreen'

// Components
import Completed from './Components/Completed'
import Home from './Components/Home/Home'
import Loading from './Components/Loading'
import BoxSelect from './Components/Record/BoxSelect/BoxSelect'
import RecordStack from './Components/Record/RecordStack';

import { FontAwesomeIcon } from '@fortawesome/react-native-fontawesome'
import { faCamera } from '@fortawesome/free-solid-svg-icons/faCamera'
import { faFolder } from "@fortawesome/free-solid-svg-icons/faFolder"
import { faHome } from "@fortawesome/free-solid-svg-icons/faHome"
import { faBars } from "@fortawesome/free-solid-svg-icons/faBars"
import GestureDemo from './Components/Record/Test';


const Tab = createDrawerNavigator()
const navigationRef = createNavigationContainerRef()

const Hola = () => (
    <Text>HOLA</Text>
)

function App() {

    const isDarkMode = useColorScheme() === 'dark';

    const backgroundStyle = {
        backgroundColor: isDarkMode ? Colors.darker : Colors.lighter,
    };

    return (
        <View style={{flex:1}}> 
            <StatusBar barStyle={isDarkMode ? 'light-content' : 'dark-content'} backgroundColor={backgroundStyle.backgroundColor}/>
            <View style={styles.menu}>
                <FontAwesomeIcon icon={faBars}/>
            </View>
            <NavigationContainer ref={navigationRef}>
                <Tab.Navigator screenOptions={({ route }) => ({
                    tabBarIcon: ({ focused, color, size }) => {
                        let iconName;
                        if(route.name==="Home") iconName = faHome
                        if(route.name==="Camera") iconName = faCamera
                        if(route.name==="Files") iconName = faFolder
                        return <FontAwesomeIcon icon={iconName} color={color}/>
                    },
                    tabBarActiveTintColor: "#3b82f6",
                    tabBarInactiveTintColor: "#979797",
                    headerShown: false
                })}>
                    <Tab.Screen name="Home" options={{ title: "Home" }} component={Home}/>
                    <Tab.Screen name="Camera" options={{ title: "Camera" }} component={RecordStack}/>
                </Tab.Navigator>
            </NavigationContainer>
        </View> 
    )
}

const styles = StyleSheet.create({
    menu: {
        position: "absolute",
        top: 10,
        left: 10
    }
})

export default App;