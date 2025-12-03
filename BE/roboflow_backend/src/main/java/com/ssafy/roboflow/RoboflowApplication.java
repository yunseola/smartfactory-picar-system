package com.ssafy.roboflow;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class RoboflowApplication {

	public static void main(String[] args) {
		SpringApplication.run(RoboflowApplication.class, args);
	}

}
