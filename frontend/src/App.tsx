import 'react-native-gesture-handler';
import React, { useState } from 'react'
import { Button, StatusBar, Text, useColorScheme, View, StyleSheet, Pressable } from 'react-native'
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
import { faBars } from "@fortawesome/free-solid-svg-icons/faBars"

const navigationRef = createNavigationContainerRef()

const Hola = () => (
    <Text>HOLA</Text>
)

function App() {

    const Drawer = createDrawerNavigator()

    const isDarkMode = useColorScheme() === 'dark';

    const backgroundStyle = {
        backgroundColor: isDarkMode ? Colors.darker : Colors.lighter,
    };

    return (
        <View style={{flex:1}}> 
            <StatusBar barStyle={isDarkMode ? 'light-content' : 'dark-content'} backgroundColor={backgroundStyle.backgroundColor}/>
            {/* <View style={styles.menu}>
                <FontAwesomeIcon icon={faBars}/>
            </View> */}
            <NavigationContainer ref={navigationRef}>
                <Drawer.Navigator initialRouteName='Home' screenOptions={{ drawerStyle: { backgroundColor: 'white' }, drawerPosition: 'right' }}>
                    <Drawer.Screen name="Home" options={{ title: "Home" }} component={Home}/>
                    <Drawer.Screen name="Camera" options={{ title: "Camera" }} component={RecordStack}/>
                </Drawer.Navigator>
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


// function HomeScreen({ navigation }) {
//   return (
//     <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
//         <Pressable style={styles.menu} onPress={() => {console.log("hello: ", navigation.openDrawer);navigation.openDrawer()}}>
//             <FontAwesomeIcon icon={faBars} size={30} color="#3b82f6"/>
//         </Pressable>
//       <Button
//         onPress={() => navigation.navigate('Notifications')}
//         title="Go to notifications"
//       />
//     </View>
//   );
// }

// function NotificationsScreen({ navigation }) {
//   return (
//     <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
//       <Button onPress={() => navigation.goBack()} title="Go back home" />
//     </View>
//   );
// }

// const Drawer = createDrawerNavigator();

// export default function App() {
//   return (
//     <NavigationContainer>
//       <Drawer.Navigator initialRouteName="Home">
//         <Drawer.Screen name="Home" component={HomeScreen} />
//         <Drawer.Screen name="Notifications" component={NotificationsScreen} />
//       </Drawer.Navigator>
//     </NavigationContainer>
//   );
// }